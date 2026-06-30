import pytest

from erinys_qwen_agent.qwen_adapter import QwenAdapter, QwenConfigurationError
from erinys_qwen_agent.qwen_adapter import clean_api_key


def clear_qwen_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ["DASHSCOPE_API_KEY", "QWEN_API_KEY"]:
        monkeypatch.setenv(key, "")


def test_mock_mode_uses_safe_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_qwen_env(monkeypatch)
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "true")

    adapter = QwenAdapter()

    assert adapter.mode() == "mock"
    assert "do not have the remembered facts" in adapter.complete("system", "user")


def test_live_mode_without_key_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_qwen_env(monkeypatch)
    monkeypatch.setenv("ERINYS_USE_MOCK_QWEN", "false")

    adapter = QwenAdapter()

    assert adapter.mode() == "misconfigured"
    with pytest.raises(QwenConfigurationError):
        adapter.complete("system", "user")


def test_clean_api_key_accepts_common_clipboard_formats() -> None:
    assert clean_api_key("Bearer sk-example") == "sk-example"
    assert clean_api_key("QWEN_API_KEY=sk-example") == "sk-example"
