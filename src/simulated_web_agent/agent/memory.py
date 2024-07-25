from abc import ABC, abstractmethod
from math import exp

import numpy as np
import openai

from . import gpt


class Memory:
    memories: list["MemoryPiece"] = []
    embeddings: np.ndarray
    timestamp: int

    def __init__(self):
        self.memories = []
        self.embeddings = None
        self.timestamp = 0

    def add_memory_piece(self, memory_piece):
        memory_piece.timestamp = self.timestamp
        self.memories.append(memory_piece)

    def update(self):
        if self.embeddings is not None and len(self.memories) == len(self.embeddings):
            return
        # first get memories with no embeddings
        memory_to_embed = self.memories[
            len(self.embeddings) if self.embeddings is not None else 0 :
        ]
        inputs = [m.content for m in memory_to_embed]
        embeds = gpt.embed_text(inputs)
        embeds = [e.embedding for e in embeds.data]
        embeds = np.array(embeds)
        for i, m in enumerate(memory_to_embed):
            m.embedding = embeds[i]
        if self.embeddings is None:
            self.embeddings = embeds
        else:
            self.embeddings = np.concatenate([self.embeddings, embeds])

    def retrieve(
        self, query, n=20, include_recent_observation=False, include_recent_action=False
    ):
        self.update()
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
        query_embedding = gpt.embed_text(query).data[0].embedding
        similarities = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(-similarities)[:n]
        return results + [self.memories[i] for i in top_indices]


class MemoryPiece(ABC):
    kind: str
    content: str
    embedding: np.ndarray
    memory: Memory
    timestamp: int

    def __init__(self, content, memory):
        self.kind = self.__class__.__name__.lower()
        self.embedding = None
        self.memory = memory
        self.content = content
        self.memory.add_memory_piece(self)

    @property
    @abstractmethod
    def importance(self):
        pass

    @importance.setter
    @abstractmethod
    def importance(self, value):
        pass


class Observation(MemoryPiece):
    original: str

    def __init__(self, content, memory, original):
        super().__init__(content, memory)
        self.original = original

    @property
    def importance(self):
        return exp(self.timestamp - self.memory.timestamp)


class Reflection(MemoryPiece):
    target: list[MemoryPiece]
    _importance: float

    def __init__(self, content, memory, target=None):
        super().__init__(content, memory)
        self.target = target
        self._importance = 0

    @property
    def importance(self):
        return self._importance

    @importance.setter
    def importance(self, value):
        self._importance = value


class Plan(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)

    @property
    def importance(self):
        return exp(self.timestamp - self.memory.timestamp)


class Action(MemoryPiece):
    raw_action: dict

    def __init__(self, content, memory, raw_action):
        super().__init__(content, memory)
        self.raw_action = raw_action

    @property
    def importance(self):
        return exp(self.timestamp - self.memory.timestamp)


class Thought(MemoryPiece):
    def __init__(self, content, memory):
        super().__init__(content, memory)

    @property
    def importance(self):
        return exp(self.timestamp - self.memory.timestamp)
