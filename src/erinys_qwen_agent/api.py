"""FastAPI app for the ERINYS Care Memory demo."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .demo import run_benchmark
from .memory_engine import govern_memories, load_memories, runtime_status, selected_ids
from .memory_store import append_user_memory, load_all_memories, load_user_memories
from .qwen_adapter import QwenAdapter, QwenConfigurationError, QwenRequestError
from .schemas import (
    AgentRequest,
    BenchmarkResponse,
    GovernanceResponse,
    HealthResponse,
    MemoryCreateRequest,
    MemoryCreateResponse,
    MemoryInventoryResponse,
)

DEFAULT_SEED = Path(__file__).resolve().parents[2] / "data" / "demo" / "care_memory.seed.json"
DEFAULT_STORE = Path(__file__).resolve().parents[2] / "data" / "demo" / "runtime_memory.json"


def allowed_origins() -> list[str]:
    raw = os.getenv("ERINYS_ALLOWED_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="ERINYS Care Memory", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["content-type"],
)


def web_dist_path() -> Path | None:
    raw_path = os.getenv("ERINYS_WEB_DIST", "")
    if not raw_path:
        return None
    path = Path(raw_path)
    return path if (path / "index.html").is_file() else None


def frontend_file(dist: Path, path_name: str) -> Path:
    root = dist.resolve()
    candidate = (dist / path_name).resolve()
    if path_name and candidate.is_file() and root in candidate.parents:
        return candidate
    return root / "index.html"


def mount_static_frontend() -> None:
    dist = web_dist_path()
    if dist is None:
        return
    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")


mount_static_frontend()


def seed_path() -> Path:
    return Path(os.getenv("ERINYS_DEMO_SEED", str(DEFAULT_SEED)))


def store_path() -> Path:
    return Path(os.getenv("ERINYS_MEMORY_STORE", str(DEFAULT_STORE)))


@app.get("/health")
def health() -> HealthResponse:
    qwen = QwenAdapter().status()
    persisted = len(load_user_memories(store_path()))
    return HealthResponse(
        status="ok",
        seed=str(seed_path()),
        qwen=qwen,
        erinys=runtime_status(),
        persisted_memories=persisted,
    )


@app.get("/memories")
def memories() -> MemoryInventoryResponse:
    seed = load_memories(seed_path())
    user = load_user_memories(store_path())
    return MemoryInventoryResponse(
        seed_count=len(seed),
        user_memory_count=len(user),
        total_count=len(seed) + len(user),
        store=str(store_path()),
        memories=[*seed, *user],
    )


@app.post("/memories")
def create_memory(request: MemoryCreateRequest) -> MemoryCreateResponse:
    memory = append_user_memory(store_path(), request, load_memories(seed_path()))
    return MemoryCreateResponse(
        memory=memory,
        persisted=True,
        store=str(store_path()),
        user_memory_count=len(load_user_memories(store_path())),
    )


@app.get("/run/governance")
def governance() -> GovernanceResponse:
    memories = load_all_memories(seed_path(), store_path())
    decisions = govern_memories(memories)
    return GovernanceResponse(
        scenario="care_visit",
        selected_ids=selected_ids(decisions),
        decisions=decisions,
        erinys=runtime_status(),
    )


@app.post("/run/benchmark")
def benchmark(request: AgentRequest) -> BenchmarkResponse:
    try:
        return run_benchmark(request, seed_path(), store_path())
    except QwenConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except QwenRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/{path_name:path}", include_in_schema=False)
def frontend(path_name: str) -> FileResponse:
    dist = web_dist_path()
    if dist is None:
        raise HTTPException(status_code=404, detail="Frontend build is not configured.")
    return FileResponse(frontend_file(dist, path_name))
