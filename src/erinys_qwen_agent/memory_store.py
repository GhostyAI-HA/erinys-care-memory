"""Persistent user memory store for the hackathon demo."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from .memory_engine import load_memories, validate_memory_graph
from .schemas import MemoryCreateRequest, MemoryRecord


class UserMemoryStore(BaseModel):
    memories: list[MemoryRecord] = Field(default_factory=list)


def load_user_memories(store_path: Path) -> list[MemoryRecord]:
    if not store_path.exists():
        return []
    data = json.loads(store_path.read_text(encoding="utf-8"))
    return UserMemoryStore.model_validate(data).memories


def load_all_memories(seed_path: Path, store_path: Path) -> list[MemoryRecord]:
    return [*load_memories(seed_path), *load_user_memories(store_path)]


def append_user_memory(
    store_path: Path, request: MemoryCreateRequest, baseline: list[MemoryRecord]
) -> MemoryRecord:
    memories = load_user_memories(store_path)
    memory = request_to_memory(request, next_memory_id(memories))
    validate_memory_graph([*baseline, *memories, memory])
    save_user_memories(store_path, [*memories, memory])
    return memory


def request_to_memory(request: MemoryCreateRequest, memory_id: str) -> MemoryRecord:
    payload = request.model_dump()
    return MemoryRecord(id=memory_id, **payload)


def next_memory_id(memories: list[MemoryRecord]) -> str:
    return f"u{len(memories) + 1:03d}"


def save_user_memories(store_path: Path, memories: list[MemoryRecord]) -> None:
    store_path.parent.mkdir(parents=True, exist_ok=True)
    payload = UserMemoryStore(memories=memories).model_dump(mode="json")
    store_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
