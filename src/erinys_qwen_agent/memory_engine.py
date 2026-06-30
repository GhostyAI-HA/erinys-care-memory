"""Deterministic memory governance for the demo."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from .schemas import ErinysStatus, MemoryDecision, MemoryRecord, MemoryStatus

TOKEN_DIVISOR = 4
SELECT_THRESHOLD = 8


class GovernanceConfig(BaseModel):
    token_divisor: int = Field(default=TOKEN_DIVISOR, ge=1)
    select_threshold: int = Field(default=SELECT_THRESHOLD, ge=1)


class ErinysPolicyRuntime(BaseModel):
    name: str = "erinys-policy-runtime"
    version: str = "1.0.0"
    policy: str = "select-current-block-private-demote-stale"
    config: GovernanceConfig = Field(default_factory=GovernanceConfig)

    def govern(self, memories: list[MemoryRecord]) -> list[MemoryDecision]:
        validate_memory_graph(memories)
        decisions = [self.decide(memory) for memory in memories]
        return sorted(decisions, key=decision_sort_key, reverse=True)

    def decide(self, memory: MemoryRecord) -> MemoryDecision:
        if memory.sensitive:
            return make_decision(memory, MemoryStatus.BLOCKED, decision_reason(memory), 0)
        if memory.contradicts:
            return make_decision(memory, MemoryStatus.CONTRADICTION, decision_reason(memory), 1)
        if memory.stale:
            return make_decision(memory, MemoryStatus.DEMOTED, decision_reason(memory), 2)
        return self.score_memory(memory)

    def score_memory(self, memory: MemoryRecord) -> MemoryDecision:
        score = float(memory.importance + memory.recency)
        status = selected_status(score, self.config.select_threshold)
        reason = decision_reason(memory) if status == MemoryStatus.SELECTED else ignored_reason(memory)
        return make_decision(memory, status, reason, score)

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // self.config.token_divisor)

    def status(self) -> ErinysStatus:
        return ErinysStatus(
            provider="erinys",
            runtime=self.name,
            version=self.version,
            policy=self.policy,
            select_threshold=self.config.select_threshold,
            token_divisor=self.config.token_divisor,
        )


DEFAULT_RUNTIME = ErinysPolicyRuntime()


def load_memories(seed_path: Path) -> list[MemoryRecord]:
    data = json.loads(seed_path.read_text(encoding="utf-8"))
    return [MemoryRecord.model_validate(item) for item in data["memories"]]


def estimate_tokens(text: str) -> int:
    return DEFAULT_RUNTIME.estimate_tokens(text)


def decide_memory(memory: MemoryRecord) -> MemoryDecision:
    return DEFAULT_RUNTIME.decide(memory)


def make_decision(
    memory: MemoryRecord, status: MemoryStatus, reason: str, score: float
) -> MemoryDecision:
    return MemoryDecision(memory=memory, status=status, reason=reason, score=score)


def score_memory(memory: MemoryRecord) -> MemoryDecision:
    return DEFAULT_RUNTIME.score_memory(memory)


def selected_status(score: float, threshold: int) -> MemoryStatus:
    if score >= threshold:
        return MemoryStatus.SELECTED
    return MemoryStatus.IGNORED


def decision_reason(memory: MemoryRecord) -> str:
    if memory.decision_note:
        return memory.decision_note
    if memory.sensitive:
        return "Blocked before Qwen because it is a private identifier."
    if memory.contradicts:
        return f"Withheld because it conflicts with newer memory {memory.contradicts}."
    if memory.stale:
        return "Demoted because the routine is outdated."
    return "Selected because it is current, actionable care context."


def ignored_reason(memory: MemoryRecord) -> str:
    if memory.decision_note:
        return memory.decision_note
    return "Ignored because it is low-priority context for this visit."


def govern_memories(memories: list[MemoryRecord]) -> list[MemoryDecision]:
    return DEFAULT_RUNTIME.govern(memories)


def selected_text(decisions: list[MemoryDecision]) -> list[str]:
    return [
        decision.memory.text
        for decision in decisions
        if decision.status == MemoryStatus.SELECTED
    ]


def selected_ids(decisions: list[MemoryDecision]) -> list[str]:
    return [
        decision.memory.id
        for decision in decisions
        if decision.status == MemoryStatus.SELECTED
    ]


def runtime_status() -> ErinysStatus:
    return DEFAULT_RUNTIME.status()


def validate_memory_graph(memories: list[MemoryRecord]) -> None:
    ids = {memory.id for memory in memories}
    missing = [memory.contradicts for memory in memories if unknown_reference(memory, ids)]
    if missing:
        raise ValueError(f"unknown contradiction reference: {', '.join(missing)}")


def unknown_reference(memory: MemoryRecord, ids: set[str]) -> bool:
    return memory.contradicts is not None and memory.contradicts not in ids


def decision_sort_key(decision: MemoryDecision) -> tuple[float, int]:
    return (decision.score, status_weight(decision.status))


def status_weight(status: MemoryStatus) -> int:
    weights = {
        MemoryStatus.SELECTED: 5,
        MemoryStatus.IGNORED: 4,
        MemoryStatus.DEMOTED: 3,
        MemoryStatus.CONTRADICTION: 2,
        MemoryStatus.BLOCKED: 1,
    }
    return weights[status]
