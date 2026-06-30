"""Smoke-test a deployed ERINYS Care Memory endpoint."""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib import request

from pydantic import BaseModel

DEFAULT_PROMPT = (
    "Draft the exact door-to-door plan for tomorrow's clinic visit using only what you "
    "remember. Include timing, transport, what to bring, questions to ask, and what not "
    "to expose. If you lack the memory, say what cannot be known instead of giving a "
    "generic checklist."
)


class QwenHealth(BaseModel):
    mode: str
    model: str
    api_key_configured: bool


class Health(BaseModel):
    status: str
    qwen: QwenHealth
    persisted_memories: int


class Run(BaseModel):
    mode: str
    answer: str
    prompt_tokens_estimate: int


class Benchmark(BaseModel):
    request: str
    runs: list[Run]


def api_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def read_json(url: str) -> dict[str, Any]:
    with request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(url: str, payload: dict[str, str]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"content-type": "application/json"})
    with request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def assert_benchmark(result: Benchmark) -> None:
    modes = {run.mode for run in result.runs}
    expected = {"no_memory", "raw_memory", "erinys_qwen"}
    if modes != expected:
        raise SystemExit(f"Unexpected benchmark modes: {sorted(modes)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="Public Alibaba Cloud endpoint URL")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    health = Health.model_validate(read_json(api_url(args.base_url, "/health")))
    benchmark = Benchmark.model_validate(
        post_json(api_url(args.base_url, "/run/benchmark"), {"request": DEFAULT_PROMPT})
    )
    assert_benchmark(benchmark)
    print(json.dumps({"health": health.model_dump(), "runs": len(benchmark.runs)}, indent=2))


if __name__ == "__main__":
    main()
