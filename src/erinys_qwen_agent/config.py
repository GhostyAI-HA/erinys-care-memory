"""Local configuration loading without exposing secret values."""

from __future__ import annotations

import os
from pathlib import Path

ENV_KEYS = frozenset(
    {
        "DASHSCOPE_API_KEY",
        "ERINYS_DEMO_SEED",
        "ERINYS_USE_MOCK_QWEN",
        "QWEN_API_KEY",
        "QWEN_BASE_URL",
        "QWEN_MODEL",
    }
)
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_local_env(env_path: Path | None = None) -> None:
    path = env_path or project_root() / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        key, value = parse_env_line(line)
        if key in ENV_KEYS and key not in os.environ:
            os.environ[key] = value


def parse_env_line(line: str) -> tuple[str, str]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return "", ""
    key, value = stripped.split("=", 1)
    return key.strip(), clean_env_value(value)


def clean_env_value(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped[1:-1]
    return stripped


def env_bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).lower() in TRUE_VALUES
