from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from erinys_qwen_agent.api import app


def test_health_exposes_qwen_and_erinys_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "true")
    client = TestClient(app)

    data = client.get("/health").json()

    assert data["status"] == "ok"
    assert data["qwen"]["provider"] == "qwen-cloud"
    assert data["erinys"]["provider"] == "erinys"
    assert data["erinys"]["runtime"] == "erinys-policy-runtime"
    assert data["erinys"]["policy"] == "select-current-block-private-demote-stale"
    assert data["persisted_memories"] >= 0


def test_governance_endpoint_returns_selected_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "true")
    client = TestClient(app)

    data = client.get("/run/governance").json()

    assert data["scenario"] == "care_visit"
    assert "m001" in data["selected_ids"]
    assert "m008" not in data["selected_ids"]
    assert len(data["decisions"]) >= 31


def test_persistent_memory_is_saved_and_reused(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "true")
    monkeypatch.setenv("ERINYS_MEMORY_STORE", str(tmp_path / "runtime_memory.json"))
    client = TestClient(app)

    saved = client.post("/memories", json={"text": PERSISTENT_MEMORY}).json()
    benchmark = client.post("/run/benchmark", json={"request": REQUEST}).json()
    governed = next(run for run in benchmark["runs"] if run["mode"] == "erinys_qwen")

    assert saved["persisted"] is True
    assert saved["memory"]["id"] == "u001"
    assert "u001" in governed["used_memories"]
    assert "wheelchair assistance" in governed["answer"]


REQUEST = "Draft tomorrow's exact clinic visit plan."
PERSISTENT_MEMORY = "Ask reception to arrange wheelchair assistance at the north entrance before check-in."
