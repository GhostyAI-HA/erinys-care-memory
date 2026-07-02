from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "generate_elevenlabs_voice.py"


def load_voice_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("generate_elevenlabs_voice", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load generate_elevenlabs_voice.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_estimate_duration_seconds_uses_target_wpm() -> None:
    module = load_voice_module()
    text = " ".join(["memory"] * module.DEFAULT_TARGET_WPM)
    assert module.estimate_duration_seconds(text) == 60


def test_build_payload_keeps_calm_voice_defaults() -> None:
    module = load_voice_module()
    payload = module.build_payload("ERINYS governs memory.", "eleven_multilingual_v2")
    assert payload.voice_settings.speed == 0.94
    assert payload.voice_settings.stability == 0.56
    assert payload.voice_settings.use_speaker_boost is True


def test_voiceover_script_estimate_fits_final_video() -> None:
    module = load_voice_module()
    script = Path("docs/video/erinys-caredog-voiceover-v2.txt")
    text = module.read_script(script)
    assert len(text.split()) == 325
    assert module.estimate_duration_seconds(text) == 144


def test_parse_env_line_keeps_secret_out_of_output() -> None:
    module = load_voice_module()
    assert module.parse_env_line("ELEVENLABS_API_KEY='secret'") == (
        "ELEVENLABS_API_KEY",
        "secret",
    )
    assert module.parse_env_line("# ELEVENLABS_API_KEY=secret") is None
