import asyncio
import json
import logging
from abc import ABC, abstractmethod
from math import exp

import numpy as np
import openai

from . import gpt
from .gpt import load_prompt

MEMORY_IMPORTANCE_PROMPT = load_prompt("memory_importance")
logger = logging.getLogger(__name__)


class Memory:
    memories: list["MemoryPiece"] = []
    embeddings: np.ndarray
    importance: np.ndarray
    timestamp: int

    def __init__(self, agent):
        self.memories = []
        self.embeddings = np.array([])
        self.importance = np.array([])
        self.timestamp = 0
        self.agent = agent
        self.update_lock = asyncio.Lock()

    async def add_memory_piece(self, memory_piece):
        async with self.update_lock:
            memory_piece.timestamp = self.timestamp
            self.memories.append(memory_piece)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["update_lock"]
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self.update_lock = asyncio.Lock()

    async def update(self):
        if self.embeddings is not None and len(self.memories) == len(self.embeddings):
            return
        logger.info("updating memory embeds and importance")
        # first get memories with no embeddings
        memory_to_embed = self.memories[
            len(self.embeddings) if self.embeddings is not None else 0 :
        ]
        inputs = [m.content for m in memory_to_embed]
        embeds = await gpt.embed_text(inputs)
        embeds = [e.embedding for e in embeds.data]
        embeds = np.array(embeds)
        for i, m in enumerate(memory_to_embed):
            m.embedding = embeds[i]
        if self.embeddings.size == 0:
            self.embeddings = embeds
        else:
            self.embeddings = np.concatenate([self.embeddings, embeds])
        # update importance
        memory_to_update = self.memories[len(self.importance) :]
        requests = [
            [
                {
                    "role": "system",
                    "content": MEMORY_IMPORTANCE_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "persona": self.agent.persona,
                            "intent": self.agent.intent,
                            "memory": m.content,
                            "plan": self.agent.current_plan.content
                            if self.agent.current_plan
                            else None,
                        }
                    ),
                },
            ]
            for m in memory_to_update
        ]
        responses = await asyncio.gather(
            *[
                gpt.async_chat(r, response_format={"type": "json_object"})
                for r in requests
            ]
        )
        new_importance = [
            json.loads(r.choices[0].message.content)["score"] for r in responses
        ]
        new_importance = np.array(new_importance) / 10
        if self.importance is None:
            self.importance = new_importance
        else:
            self.importance = np.concatenate([self.importance, new_importance])
        for i, m in enumerate(memory_to_update):
            m.importance = new_importance[i]

    async def retrieve(
        self,
        query,
        n=20,
        include_recent_observation=False,
        include_recent_action=False,
        kind_weight={},
    ):
        async with self.update_lock:
            await self.update()
            results = []
            if include_recent_observation:
                # must include the most recent observation
                results += [
                    m
                    for m in self.memories
                    if m.kind == "observation" and m.timestamp == self.timestamp
                ]
            if include_recent_action:
                # must include the most recent action
                results += [
                    m
                    for m in self.memories
                    if m.kind == "action" and m.timestamp >= self.timestamp - 5
                ]
            query_embedding = (await gpt.embed_text(query)).data[0].embedding
            similarities = np.dot(self.embeddings, query_embedding)
            recencies = np.array([m.timestamp - self.timestamp for m in self.memories])
            recencies = np.exp(recencies)
            kind_weights = np.array([kind_weight.get(m.kind, 1) for m in self.memories])
            scores = (similarities + recencies + self.importance) * kind_weights
            top_indices = np.argsort(-scores)[:n]
            return results + [self.memories[i] for i in top_indices]


class MemoryPiece(ABC):
    kind: str
    content: str
    embedding: np.ndarray
    importance: float
    memory: Memory
    timestamp: int

    def __init__(self, content, memory):
        self.kind = self.__class__.__name__.lower()
        self.embedding = np.array([])  # Initialize with an empty numpy array
        self.importance = -1
        self.memory = memory
        self.content = content
        # self.memory.add_memory_piece(self)


class Observation(MemoryPiece):
    original: str

    def __init__(self, content, memory, original):
        super().__init__(content, memory)
        self.original = original


class Reflection(MemoryPiece):
    target: list[MemoryPiece]

    def __init__(self, content, memory, target: list[MemoryPiece]):
        super().__init__(content, memory)
        self.target = target


class Plan(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)


class Action(MemoryPiece):
    raw_action: dict

    def __init__(self, content, memory, raw_action):
        super().__init__(content, memory)
        self.raw_action = raw_action


class Thought(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)
