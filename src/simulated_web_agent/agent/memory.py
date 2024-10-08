import asyncio
import json
import logging
from abc import ABC, abstractmethod
from math import exp

import json_fix
import numpy as np
import openai

from . import context, gpt
from .gpt import async_chat_bedrock as async_chat
from .gpt import embed_text_bedrock as embed_text
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
        self.read_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()

    async def add_memory_piece(self, memory_piece):
        # async with self.update_lock:
        memory_piece.timestamp = self.timestamp
        self.memories.append(memory_piece)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["read_lock"]
        del state["write_lock"]
        return state

    def __setstate__(self, state):
        self.__dict__ = state
        self.read_lock = asyncio.Lock()
        self.write_lock = asyncio.Lock()

    async def update(self):
        async with self.write_lock:
            if self.embeddings is not None and len(self.memories) == len(
                self.embeddings
            ):
                return
            logger.info("updating memory embeds and importance")

            async def get_embeddings():
                # first get memories with no embeddings
                memory_to_embed = self.memories[
                    len(self.embeddings) if self.embeddings is not None else 0 :
                ]
                inputs = [m.content for m in memory_to_embed]
                embeds = await embed_text(inputs)
                embeds = np.array(embeds)
                for i, m in enumerate(memory_to_embed):
                    m.embedding = embeds[i]
                return embeds

            async def update_importance():
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
                        async_chat(
                            r, response_format={"type": "json_object"}, log=False
                        )
                        for r in requests
                    ]
                )
                new_importance = [json.loads(r)["score"] for r in responses]
                new_importance = np.array(new_importance) / 10
                for i, m in enumerate(memory_to_update):
                    m.importance = new_importance[i]
                return new_importance

            embeds, new_importance = await asyncio.gather(
                get_embeddings(), update_importance()
            )
            async with self.read_lock:
                if self.embeddings.size == 0:
                    self.embeddings = embeds
                else:
                    self.embeddings = np.concatenate([self.embeddings, embeds])
                if self.importance is None:
                    self.importance = new_importance
                else:
                    self.importance = np.concatenate([self.importance, new_importance])

    async def retrieve(
        self,
        query,
        n=20,
        include_recent_observation=False,
        include_recent_action=False,
        include_recent_plan=False,
        include_recent_thought=False,
        trigger_update=True,
        kind_weight={},
    ):
        if trigger_update:
            await self.update()
        async with self.read_lock:
            results = []
            if include_recent_observation:
                # must include the most recent observation
                results += [
                    m
                    for m in self.memories
                    if m.kind == "observation" and m.timestamp >= self.timestamp - 3
                ]
            if include_recent_action:
                # must include the most recent action
                results += [
                    m
                    for m in self.memories
                    if m.kind == "action" and m.timestamp >= self.timestamp - 5
                ]
            if include_recent_plan:
                results += [
                    m
                    for m in self.memories
                    if m.kind == "plan" and m.timestamp >= self.timestamp - 5
                ]
            if include_recent_thought:
                results += [
                    m
                    for m in self.memories
                    if m.kind == "thought" and m.timestamp >= self.timestamp - 5
                ]
            # make a copy for read
            # embedding = self.embeddings.copy()
            # importance = self.importance.copy()
            # memories = [m for m in self.memories]
            if self.embeddings.size == 0:
                if context.api_call_manager.get():
                    context.api_call_manager.get().retrieve_result.append(results)
                return results

            query_embedding = (await embed_text([query], type="search_query"))[0]
            similarities = np.dot(self.embeddings, query_embedding)
            recencies = np.array([m.timestamp - self.timestamp for m in self.memories])
            recencies = np.exp(recencies)
            kind_weights = np.array([kind_weight.get(m.kind, 1) for m in self.memories])
            # print(similarities.size, recencies.size, self.importance.size)
            smallest_size = min(similarities.size, recencies.size, self.importance.size)
            scores = (
                similarities[:smallest_size]
                + recencies[:smallest_size]
                + self.importance[:smallest_size]
            ) * kind_weights[:smallest_size]
            # scores = (similarities + recencies + self.importance) * kind_weights
            top_indices = np.argsort(-scores)[:n]
            results += [self.memories[i] for i in top_indices]
            if context.api_call_manager.get():
                context.api_call_manager.get().retrieve_result.append(results)
            return results


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

    def __json__(self):
        return json.dumps(
            {
                "kind": self.kind,
                "content": self.content,
                "timestamp": self.timestamp,
            }
        )


class Observation(MemoryPiece):
    original: str

    def __init__(self, content, memory, original):
        super().__init__(content, memory)
        self.original = original


class Reflection(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)


class Plan(MemoryPiece):
    next_step: str

    def __init__(self, content, memory, next_step):
        super().__init__(content, memory)
        self.next_step = next_step


class Action(MemoryPiece):
    raw_action: dict

    def __init__(self, content, memory, raw_action):
        super().__init__(content, memory)
        self.raw_action = raw_action


class Thought(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)
        super().__init__(content, memory)
        super().__init__(content, memory)
