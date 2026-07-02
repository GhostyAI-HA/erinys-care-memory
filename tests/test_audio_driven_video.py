from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "build_audio_driven_video.py"


def load_audio_driven_module() -> ModuleType:
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("build_audio_driven_video", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load build_audio_driven_video.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_audio_driven_video"] = module
    spec.loader.exec_module(module)
    return module


def test_srt_time_format_uses_millisecond_commas() -> None:
    module = load_audio_driven_module()
    assert module.format_srt_time(84.188) == "00:01:24,188"


def test_create_cues_are_monotonic() -> None:
    module = load_audio_driven_module()
    durations = [1.0] * len(module.SEGMENTS)
    cues = module.create_cues(durations)
    assert len(cues) == len(module.SEGMENTS)
    assert cues[0].start == 0.0
    assert cues[-1].end == float(len(module.SEGMENTS))
