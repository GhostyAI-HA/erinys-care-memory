"""Pydantic schemas for the MemoryAgent demo."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class MemoryStatus(StrEnum):
    SELECTED = "selected"
    IGNORED = "ignored"
    DEMOTED = "demoted"
    BLOCKED = "blocked"
    CONTRADICTION = "contradiction"


class MemoryRecord(BaseModel):
    id: str
    text: str
    kind: Literal["preference", "constraint", "event", "outdated", "sensitive"]
    importance: int = Field(ge=1, le=5)
    recency: int = Field(ge=1, le=5)
    sensitive: bool = False
    stale: bool = False
    contradicts: str | None = None
    decision_note: str | None = None


class MemoryCreateRequest(BaseModel):
    text: str = Field(min_length=8, max_length=500)
    kind: Literal["preference", "constraint", "event", "outdated", "sensitive"] = "event"
    importance: int = Field(default=5, ge=1, le=5)
    recency: int = Field(default=5, ge=1, le=5)
    sensitive: bool = False
    stale: bool = False
    contradicts: str | None = None
    decision_note: str | None = None


class MemoryCreateResponse(BaseModel):
    memory: MemoryRecord
    persisted: bool
    store: str
    user_memory_count: int


class MemoryInventoryResponse(BaseModel):
    seed_count: int
    user_memory_count: int
    total_count: int
    store: str
    memories: list[MemoryRecord]


class MemoryDecision(BaseModel):
    memory: MemoryRecord
    status: MemoryStatus
    reason: str
    score: float


class ErinysStatus(BaseModel):
    provider: Literal["erinys"]
    runtime: str
    version: str
    policy: str
    select_threshold: int
    token_divisor: int


class AgentRequest(BaseModel):
    request: str
    scenario: str = "care_visit"


class AgentRun(BaseModel):
    mode: Literal["no_memory", "raw_memory", "erinys_qwen"]
    answer: str
    used_memories: list[str]
    memory_decisions: list[MemoryDecision]
    prompt_tokens_estimate: int


class BenchmarkResponse(BaseModel):
    request: str
    runs: list[AgentRun]


class GovernanceResponse(BaseModel):
    scenario: str
    selected_ids: list[str]
    decisions: list[MemoryDecision]
    erinys: ErinysStatus


class QwenStatus(BaseModel):
    provider: str
    model: str
    base_url: str
    api_key_configured: bool
    mock_requested: bool
    mode: Literal["mock", "misconfigured", "live"]


class HealthResponse(BaseModel):
    status: str
    seed: str
    qwen: QwenStatus
    erinys: ErinysStatus
    persisted_memories: int
