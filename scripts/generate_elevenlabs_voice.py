#!/usr/bin/env python3
"""Generate ERINYS CareDog narration with ElevenLabs.

The script never prints API keys. Set ELEVENLABS_API_KEY in the environment and
pass a voice id explicitly, or set ELEVENLABS_VOICE_ID.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Literal
from urllib import error, parse, request

from pydantic import BaseModel, Field


API_BASE = "https://api.elevenlabs.io"
DEFAULT_MODEL_ID = "eleven_multilingual_v2"
DEFAULT_OUTPUT_FORMAT = "mp3_44100_128"
DEFAULT_SEED = 310762
DEFAULT_TARGET_WPM = 135
DEFAULT_SCRIPT = Path("docs/video/erinys-caredog-voiceover-v2.txt")
DEFAULT_OUTPUT = Path("docs/video/build/erinys-caredog-voiceover-v2.mp3")


class VoiceSettings(BaseModel):
    """Per-request voice settings for calm documentary narration."""

    stability: float = Field(default=0.56, ge=0, le=1)
    similarity_boost: float = Field(default=0.78, ge=0, le=1)
    style: float = Field(default=0.08, ge=0, le=1)
    use_speaker_boost: bool = True
    speed: float = Field(default=0.94, ge=0.7, le=1.2)


class SpeechPayload(BaseModel):
    """Validated ElevenLabs text-to-speech request payload."""

    text: str = Field(min_length=1)
    model_id: str = DEFAULT_MODEL_ID
    voice_settings: VoiceSettings = Field(default_factory=VoiceSettings)
    seed: int = Field(default=DEFAULT_SEED, ge=0, le=4_294_967_295)
    apply_text_normalization: Literal["auto", "on", "off"] = "auto"


class VoiceSummary(BaseModel):
    """Small safe subset of the ElevenLabs voices response."""

    voice_id: str
    name: str
    category: str | None = None
    preview_url: str | None = None
    labels: dict[str, str] = Field(default_factory=dict)


VoiceSettings.model_rebuild()
SpeechPayload.model_rebuild()
VoiceSummary.model_rebuild()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, default=DEFAULT_SCRIPT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--voice-id", default=os.getenv("ELEVENLABS_VOICE_ID"))
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def read_script(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Voice script is empty: {path}")
    return text


def require_api_key() -> str:
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set.")
    return api_key


def parse_env_line(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip().strip("\"'")


def load_env_file(path: Path | None) -> None:
    if path is None or not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_env_line(line)
        if parsed and parsed[0].startswith("ELEVENLABS_"):
            os.environ.setdefault(parsed[0], parsed[1])


def estimate_duration_seconds(text: str) -> int:
    words = len(text.split())
    return round(words / DEFAULT_TARGET_WPM * 60)


def build_payload(text: str, model_id: str) -> SpeechPayload:
    return SpeechPayload(text=text, model_id=model_id)


def request_bytes(url: str, api_key: str, payload: SpeechPayload) -> bytes:
    data = payload.model_dump_json().encode("utf-8")
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    req = request.Request(url=url, data=data, headers=headers, method="POST")
    with request.urlopen(req, timeout=120) as response:
        return response.read()


def speech_url(voice_id: str) -> str:
    query = parse.urlencode({"output_format": DEFAULT_OUTPUT_FORMAT})
    return f"{API_BASE}/v1/text-to-speech/{voice_id}?{query}"


def write_audio(output_path: Path, audio_bytes: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(audio_bytes)


def generate_audio(args: argparse.Namespace, text: str) -> Path:
    if not args.voice_id:
        raise RuntimeError("Pass --voice-id or set ELEVENLABS_VOICE_ID.")
    payload = build_payload(text, args.model_id)
    audio = request_bytes(speech_url(args.voice_id), require_api_key(), payload)
    write_audio(args.output, audio)
    return args.output


def voices_url() -> str:
    return f"{API_BASE}/v2/voices"


def load_voices(api_key: str) -> list[VoiceSummary]:
    req = request.Request(voices_url(), headers={"xi-api-key": api_key})
    with request.urlopen(req, timeout=60) as response:
        body = json.loads(response.read().decode("utf-8"))
    return [VoiceSummary.model_validate(item) for item in body.get("voices", [])]


def print_voices() -> None:
    voices = load_voices(require_api_key())
    for voice in voices:
        labels = ", ".join(f"{key}={value}" for key, value in voice.labels.items())
        print(f"{voice.name}\t{voice.voice_id}\t{voice.category or '-'}\t{labels}")


def print_dry_run(args: argparse.Namespace, text: str) -> None:
    payload = build_payload(text, args.model_id)
    print(f"script_words={len(text.split())}")
    print(f"estimated_seconds={estimate_duration_seconds(text)}")
    print(f"model_id={payload.model_id}")
    print(f"output={args.output}")
    print(f"voice_id={'set' if args.voice_id else 'missing'}")


def main() -> int:
    args = parse_args()
    load_env_file(args.env_file)
    args.voice_id = args.voice_id or os.getenv("ELEVENLABS_VOICE_ID")
    if args.list_voices:
        print_voices()
        return 0
    text = read_script(args.script)
    if args.dry_run:
        print_dry_run(args, text)
        return 0
    try:
        print(f"wrote={generate_audio(args, text)}")
        return 0
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:800]
        raise RuntimeError(f"ElevenLabs HTTP {exc.code}: {body}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
