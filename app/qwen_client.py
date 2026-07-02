from __future__ import annotations

import json
import os
from urllib import error, request


DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.7-plus"
DEFAULT_MAX_TOKENS = 240
DEFAULT_TIMEOUT_SECONDS = 90


class QwenClient:
    def __init__(self) -> None:
        self.api_key = os.environ.get("QWEN_API_KEY") or os.environ.get("DASHSCOPE_API_KEY")
        self.base_url = os.environ.get("QWEN_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        self.model = os.environ.get("QWEN_MODEL", DEFAULT_MODEL)
        self.live_enabled = os.environ.get("QWEN_LIVE", "1") != "0"
        self.max_tokens = int(os.environ.get("QWEN_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
        self.timeout_seconds = float(os.environ.get("QWEN_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))

    @property
    def can_call(self) -> bool:
        return bool(self.api_key and self.live_enabled)

    def complete(self, prompt: str, *, temperature: float = 0.15) -> tuple[str, str | None]:
        if not self.can_call:
            return "", "QWEN_API_KEY is not configured or QWEN_LIVE=0."

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are precise, privacy-aware, and concise. "
                        "For this demo, do not reveal private synthetic identifiers unless explicitly present in ungoverned raw memory context."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        encoded = json.dumps(payload).encode("utf-8")
        call = request.Request(f"{self.base_url}/chat/completions", data=encoded, headers=headers, method="POST")
        try:
            with request.urlopen(call, timeout=self.timeout_seconds) as response:  # nosec B310 - caller controls endpoint env.
                data = json.loads(response.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"], None
        except error.HTTPError as exc:  # pragma: no cover - network/provider dependent
            detail = exc.read().decode("utf-8", errors="replace")
            return "", f"HTTPError {exc.code}: {detail[:400]}"
        except Exception as exc:  # pragma: no cover - network/provider dependent
            return "", f"{type(exc).__name__}: {exc}"
