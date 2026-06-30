"""Qwen Cloud OpenAI-compatible adapter with a safe mock fallback."""

from __future__ import annotations

import os

from openai import OpenAI

from .config import env_bool, load_local_env

DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.7-plus"


class QwenConfigurationError(RuntimeError):
    """Raised when live Qwen Cloud mode is requested but not configured."""


class QwenRequestError(RuntimeError):
    """Raised when Qwen Cloud returns an error."""


class QwenAdapter:
    def __init__(self) -> None:
        load_local_env()
        self.api_key = clean_api_key(os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"))
        self.base_url = os.getenv("QWEN_BASE_URL", DEFAULT_BASE_URL)
        self.model = os.getenv("QWEN_MODEL", DEFAULT_MODEL)
        self.use_mock = env_bool("ERINYS_USE_MOCK_QWEN", True)

    def complete(self, system: str, user: str) -> str:
        if self.use_mock:
            return mock_completion(user)
        if not self.api_key:
            raise QwenConfigurationError("Qwen Cloud API key is not configured.")
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
        except Exception as exc:
            raise QwenRequestError(f"Qwen Cloud request failed: {type(exc).__name__}") from exc
        return response.choices[0].message.content or ""

    def status(self) -> dict[str, str | bool]:
        return {
            "provider": "qwen-cloud",
            "model": self.model,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "mock_requested": self.use_mock,
            "mode": self.mode(),
        }

    def mode(self) -> str:
        if self.use_mock:
            return "mock"
        if not self.api_key:
            return "misconfigured"
        return "live"


def clean_api_key(value: str | None) -> str:
    if not value:
        return ""
    key = value.strip().strip("'\"")
    if "=" in key and key.split("=", 1)[0].strip() in {"DASHSCOPE_API_KEY", "QWEN_API_KEY"}:
        key = key.split("=", 1)[1].strip().strip("'\"")
    if key.lower().startswith("bearer "):
        key = key[7:].strip()
    return key


def mock_completion(prompt: str) -> str:
    if "Selected memories" in prompt:
        persistent_note = persistent_memory_note(prompt)
        return (
            "Exact plan: arrange a 13:35 taxi pickup from the building lobby, check in at "
            "14:20, ask the driver for the accessible north entrance drop-off, and avoid "
            "stairs or long walking routes. Bring the medication notebook, blue referral "
            "folder, printed questions, and cardigan. Ask about dizziness after standing "
            "and the current medication schedule. Keep insurance, portal, door code, phone, "
            f"and address details out of the answer.{persistent_note}"
        )
    if "Raw memories" in prompt:
        return (
            "Conflicted raw plan: check in at 09:00 or 14:20, take the 8:10 train, transfer "
            "at Central, and use the east stairway to reception. The medication notebook may "
            "be optional, but also bring it. Include insurance ID SYNTH-INSURANCE-9001, portal "
            "number SYNTH-PORTAL-4420, and home address 1-2-3 Synthetic Street for coordination, "
            "then go to the spicy ramen shop after the visit."
        )
    return (
        "I do not have the remembered facts needed to draft an exact door-to-door plan. "
        "I cannot know the appointment time, pickup time, route, mobility constraints, or "
        "documents to bring without memory context."
    )


def persistent_memory_note(prompt: str) -> str:
    if "wheelchair assistance" not in prompt:
        return ""
    return " Confirm wheelchair assistance at the north entrance before check-in."
