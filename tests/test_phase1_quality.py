from pathlib import Path

import pytest

from erinys_qwen_agent.demo import SYSTEM_PROMPT, run_benchmark
from erinys_qwen_agent.memory_engine import (
    govern_memories,
    load_memories,
    runtime_status,
    selected_ids,
    selected_text,
    validate_memory_graph,
)
from erinys_qwen_agent.schemas import AgentRequest, AgentRun, MemoryDecision

SEED_PATH = Path("data/demo/care_memory.seed.json")
EXPECTED_SELECTED_IDS = {"m001", "m002", "m003", "m004", "m005", "m010", "m011", "m012", "m027"}
EXPECTED_BLOCKED_IDS = {"m008", "m009", "m013", "m014", "m015"}
EXPECTED_CONTRADICTION_IDS = {"m006", "m007", "m016", "m017", "m018"}
EXPECTED_DEMOTED_IDS = {"m019", "m020", "m025", "m026", "m030"}
EXPECTED_IGNORED_IDS = {"m021", "m022", "m023", "m024", "m028", "m029", "m031"}
GOVERNED_REQUIRED_TERMS = ("13:35", "14:20", "taxi", "north entrance", "medication notebook")
GOVERNED_FORBIDDEN_TERMS = ("SYNTH-", "1-2-3 Synthetic Street", "8:10 train", "09:00", "east stairway")
RAW_FAILURE_TERMS = ("SYNTH-INSURANCE-9001", "SYNTH-PORTAL-4420", "1-2-3 Synthetic Street", "8:10 train")
REQUEST = (
    "Draft the exact door-to-door plan for tomorrow's clinic visit using only what you remember. "
    "Include timing, transport, what to bring, questions to ask, and what not to expose. "
    "If you lack the memory, say what cannot be known instead of giving a generic checklist."
)


def test_memory_governance_has_judge_visible_decisions() -> None:
    decisions = govern_memories(load_memories(SEED_PATH))
    counts = {status: sum(decision.status == status for decision in decisions) for status in STATUSES}

    assert counts["selected"] >= 8
    assert counts["contradiction"] >= 4
    assert counts["blocked"] >= 4
    assert counts["demoted"] >= 3


def test_memory_governance_routes_expected_records() -> None:
    grouped = group_decisions(govern_memories(load_memories(SEED_PATH)))

    assert grouped["selected"] == EXPECTED_SELECTED_IDS
    assert grouped["blocked"] == EXPECTED_BLOCKED_IDS
    assert grouped["contradiction"] == EXPECTED_CONTRADICTION_IDS
    assert grouped["demoted"] == EXPECTED_DEMOTED_IDS
    assert grouped["ignored"] == EXPECTED_IGNORED_IDS


def test_erinys_runtime_is_explicit_and_reproducible() -> None:
    status = runtime_status()

    assert status.provider == "erinys"
    assert status.runtime == "erinys-policy-runtime"
    assert status.select_threshold == 8
    assert status.token_divisor == 4


def test_seed_has_valid_contradiction_references() -> None:
    validate_memory_graph(load_memories(SEED_PATH))


def test_selected_context_excludes_private_and_stale_memory() -> None:
    decisions = govern_memories(load_memories(SEED_PATH))
    selected = "\n".join(selected_text(decisions))

    assert "14:20" in selected
    assert "13:35" in selected
    assert "SYNTH-" not in selected
    assert "8:10 train" not in selected
    assert "spicy ramen" not in selected
    assert "m008" not in selected_ids(decisions)


def test_three_modes_create_judge_obvious_contrast(monkeypatch: pytest.MonkeyPatch) -> None:
    no_memory_run, raw_run, governed_run = benchmark_runs(monkeypatch)

    assert "do not have the remembered facts" in no_memory_run.answer
    assert "13:35" not in no_memory_run.answer
    assert all(term in raw_run.answer for term in RAW_FAILURE_TERMS)
    assert all(term in governed_run.answer for term in GOVERNED_REQUIRED_TERMS)
    assert all(term not in governed_run.answer for term in GOVERNED_FORBIDDEN_TERMS)


def test_phase1_benchmark_shows_large_context_savings(monkeypatch: pytest.MonkeyPatch) -> None:
    _, raw_run, governed_run = benchmark_runs(monkeypatch)
    savings = 1 - governed_run.prompt_tokens_estimate / raw_run.prompt_tokens_estimate

    assert raw_run.prompt_tokens_estimate >= governed_run.prompt_tokens_estimate * 2
    assert savings >= 0.6


def test_governed_prompt_separates_privacy_from_care_constraints() -> None:
    assert "Privacy boundaries" in SYSTEM_PROMPT
    assert "Treat 'what not to expose' as privacy-only" in SYSTEM_PROMPT
    assert "walking distance as privacy exposure" in SYSTEM_PROMPT


def benchmark_runs(monkeypatch: pytest.MonkeyPatch) -> tuple[AgentRun, AgentRun, AgentRun]:
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "true")
    result = run_benchmark(AgentRequest(request=REQUEST), SEED_PATH)
    return (
        next(run for run in result.runs if run.mode == "no_memory"),
        next(run for run in result.runs if run.mode == "raw_memory"),
        next(run for run in result.runs if run.mode == "erinys_qwen"),
    )


def group_decisions(decisions: list[MemoryDecision]) -> dict[str, set[str]]:
    return {
        status: {decision.memory.id for decision in decisions if decision.status == status}
        for status in ALL_STATUSES
    }


ALL_STATUSES = ("selected", "contradiction", "blocked", "demoted", "ignored")
STATUSES = ("selected", "contradiction", "blocked", "demoted")
