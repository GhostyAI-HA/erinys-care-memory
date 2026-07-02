from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
from urllib.parse import urlparse

from .governance import (
    DEFAULT_REQUEST,
    BenchmarkRun,
    all_memories,
    build_governed_prompt,
    build_no_memory_prompt,
    build_raw_memory_prompt,
    estimate_tokens,
    fallback_answer,
    govern_memories,
    reset_runtime_memories,
    save_runtime_memory,
    selected_memories,
    serialize_decision,
    status_counts,
)
from .qwen_client import QwenClient


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
MAX_BODY_BYTES = 65536
ALL_MODES = {"no_memory", "raw_memory", "erinys_qwen"}
STATIC_CONTENT_TYPES = {
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".png": "image/png",
    ".webp": "image/webp",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".svg": "image/svg+xml",
}
QwenCompletion = tuple[str, str | None, str]


class Handler(BaseHTTPRequestHandler):
    server_version = "ERINYS-Care-Memory/1.0"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if path == "/health":
            self.send_json(health_payload())
            return
        if path == "/memories":
            items = all_memories()
            self.send_json({"count": len(items), "items": [asdict(item) for item in items]})
            return
        if path.startswith("/static/"):
            self.serve_static(path)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = self.read_json()
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        if path == "/memories":
            try:
                memory = save_runtime_memory(str(body.get("text", "")))
            except ValueError as exc:
                self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"ok": True, "memory": asdict(memory)})
            return
        if path == "/run/governance":
            self.send_json(governance_payload())
            return
        if path == "/run/benchmark":
            prompt = str(body.get("request") or DEFAULT_REQUEST)
            use_live_qwen = bool(body.get("use_live_qwen", True))
            live_modes = parse_live_modes(body.get("live_modes"))
            self.send_json(benchmark_payload(prompt, use_live_qwen, live_modes))
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if path == "/memories/runtime":
            reset_runtime_memories()
            self.send_json({"ok": True, "persisted_memories": 0})
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def serve_static(self, path: str) -> None:
        relative = path.removeprefix("/static/")
        target = (STATIC_DIR / relative).resolve()
        if not target.is_relative_to(STATIC_DIR.resolve()) or not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self.send_file(target, static_content_type(target), static_cache_control(target))

    def send_file(self, path: Path, content_type: str, cache_control: str = "no-store") -> None:
        data = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(data)

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        if length > MAX_BODY_BYTES:
            raise ValueError("request body too large")
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON body: {exc}") from exc

    def log_message(self, fmt: str, *args: object) -> None:
        if os.environ.get("ERINYS_ACCESS_LOG", "0") == "1":
            super().log_message(fmt, *args)


def health_payload() -> dict:
    client = QwenClient()
    decisions = govern_memories()
    return {
        "ok": True,
        "service": "ERINYS Care Memory",
        "version": "1.0.0",
        "model": client.model,
        "qwen_live_configured": client.can_call,
        "persisted_memories": len([m for m in all_memories() if m.id.startswith("u")]),
        "governance_counts": status_counts(decisions),
        "endpoints": ["/health", "/memories", "/run/governance", "/run/benchmark"],
    }


def static_content_type(path: Path) -> str:
    return STATIC_CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")


def static_cache_control(path: Path) -> str:
    if "assets" in path.parts:
        return "public, max-age=31536000, immutable"
    return "no-store"


def governance_payload() -> dict:
    decisions = govern_memories()
    return {
        "counts": status_counts(decisions),
        "selected_memories": [asdict(memory) for memory in selected_memories(decisions)],
        "decisions": [serialize_decision(decision) for decision in decisions],
    }


def benchmark_payload(user_request: str, use_live_qwen: bool = True, live_modes: set[str] | None = None) -> dict:
    client = QwenClient()
    memories_for_run = all_memories()
    decisions = govern_memories(memories_for_run)
    runs: list[BenchmarkRun] = []
    prompts = {
        "no_memory": build_no_memory_prompt(user_request),
        "raw_memory": build_raw_memory_prompt(user_request, memories_for_run),
        "erinys_qwen": build_governed_prompt(user_request, decisions),
    }

    completions = complete_prompts(client, prompts, use_live_qwen, live_modes if live_modes is not None else ALL_MODES)
    for mode in ("no_memory", "raw_memory", "erinys_qwen"):
        answer, provider_error, provider = completions[mode]
        if not answer:
            answer = fallback_answer(mode, user_request, decisions)
        used = (
            []
            if mode == "no_memory"
            else [memory.id for memory in memories_for_run]
            if mode == "raw_memory"
            else [memory.id for memory in selected_memories(decisions)]
        )
        token_estimate = estimate_tokens(prompts[mode])
        runs.append(
            BenchmarkRun(
                mode=mode,
                answer=answer,
                used_memories=used,
                memory_decisions=decisions if mode == "erinys_qwen" else [],
                prompt_tokens_estimate=token_estimate,
                provider=provider,
                model=client.model,
                provider_error=provider_error,
            )
        )

    raw_tokens = next(run.prompt_tokens_estimate for run in runs if run.mode == "raw_memory")
    governed_tokens = next(run.prompt_tokens_estimate for run in runs if run.mode == "erinys_qwen")
    reduction = round((1 - governed_tokens / raw_tokens) * 100) if raw_tokens else 0
    return {
        "request": user_request,
        "model": client.model,
        "qwen_live_configured": client.can_call,
        "token_reduction_percent": reduction,
        "governance_counts": status_counts(decisions),
        "runs": [serialize_run(run) for run in runs],
    }


def parse_live_modes(value: object) -> set[str] | None:
    if not isinstance(value, list):
        return None
    return {str(item) for item in value if str(item) in {"no_memory", "raw_memory", "erinys_qwen"}}


def complete_prompts(client: QwenClient, prompts: dict[str, str], use_live_qwen: bool, live_modes: set[str]) -> dict[str, QwenCompletion]:
    if not use_live_qwen or not client.can_call:
        return {mode: ("", None, "demo_fallback") for mode in prompts}
    fallback = {mode: ("", None, "demo_fallback") for mode in prompts if mode not in live_modes}
    live_prompts = {mode: prompt for mode, prompt in prompts.items() if mode in live_modes}
    with ThreadPoolExecutor(max_workers=len(prompts)) as pool:
        futures = {mode: pool.submit(client.complete, prompt) for mode, prompt in live_prompts.items()}
        live_results = {mode: normalize_completion(future.result()) for mode, future in futures.items()}
    return {**fallback, **live_results}


def normalize_completion(result: tuple[str, str | None]) -> QwenCompletion:
    answer, error_message = result
    provider = "qwen_cloud" if answer else "demo_fallback"
    return answer, error_message, provider


def serialize_run(run: BenchmarkRun) -> dict:
    return {
        "mode": run.mode,
        "answer": run.answer,
        "used_memories": run.used_memories,
        "memory_decisions": [serialize_decision(decision) for decision in run.memory_decisions],
        "prompt_tokens_estimate": run.prompt_tokens_estimate,
        "provider": run.provider,
        "model": run.model,
        "provider_error": run.provider_error,
    }


def main() -> None:
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"ERINYS Care Memory listening on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
