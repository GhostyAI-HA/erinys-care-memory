#!/usr/bin/env python3
"""Build the ERINYS CareDog demo with audio-driven slide timing."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

from generate_elevenlabs_voice import (
    DEFAULT_MODEL_ID,
    build_payload,
    load_env_file,
    request_bytes,
    require_api_key,
    speech_url,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_DIR = PROJECT_ROOT / "docs" / "video"
BUILD_DIR = VIDEO_DIR / "build" / "audio-driven-v1"
FINAL_VIDEO = VIDEO_DIR / "build" / "erinys-caredog-demo-final.mp4"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"
FRAME_WIDTH = 1920
FRAME_HEIGHT = 1080
FPS = "30"
END_HOLD_SECONDS = 2.4
TARGET_WPM = 135


@dataclass(frozen=True)
class Segment:
    """A narration-controlled presentation segment."""

    image: Path
    text: str
    pause: float = 0.75


@dataclass(frozen=True)
class CaptionCue:
    """Caption cue with realized audio-driven timing."""

    index: int
    start: float
    end: float
    text: str


SEGMENTS: tuple[Segment, ...] = (
    Segment(VIDEO_DIR / "erinys-caredog-title.png", "This is ERINYS CareDog, by Shun Fujiyoshi, Ghosty.AI, for the Global AI Hackathon with Qwen Cloud, Track 1 MemoryAgent.", pause=0.45),
    Segment(VIDEO_DIR / "erinys-caredog-human-moment.png", "Tomorrow at thirteen thirty five, mom has a clinic visit. The family remembers the wheelchair entrance, the medication notebook, the blue folder, and private identifiers that must never leak. The question is what should reach Qwen right now.", pause=0.55),
    Segment(VIDEO_DIR / "erinys-caredog-problem.png", "That is the pain. Family health memory is messy, sensitive, and time-dependent. A stale note can create the wrong plan. A private identifier can leak into an answer.", pause=0.6),
    Segment(VIDEO_DIR / "erinys-caredog-new-idea.png", "The new idea is simple. ERINYS governs memory before Qwen generates. It is a memory gate, not just a bigger memory store.", pause=0.65),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "00-ready.png", "Now let's view the live application running on Alibaba Cloud ECS. The public Docker demo is connected to Qwen Cloud with qwen3.7-plus."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "01-initial-no-memory.png", "We ask the same clinic-visit question across three memory strategies. First, No Memory. Qwen is careful, but it lacks the appointment and transport context."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "02-initial-raw-memory.png", "Second, Raw Memory. The answer is detailed, but unsafe. Old routines and private identifiers enter the plan."),
    Segment(VIDEO_DIR / "erinys-caredog-private-id-proof.png", "Here is the proof cut. Raw Memory exposes synthetic private IDs. ERINYS blocks those identifiers before Qwen sees the governed prompt.", pause=0.95),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "03-initial-decision-layer.png", "Now ERINYS classifies memory before Qwen sees the prompt. Each memory becomes selected, conflicted, demoted, or blocked."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "04-initial-erinys-qwen.png", "Third, ERINYS plus Qwen. Only safe, current care context reaches the final answer, so the plan becomes specific without exposing private data."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "05-save-memory.png", "Now we save a live care instruction: ask reception to arrange wheelchair assistance at the clinic entrance."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "09-saved-erinys-qwen.png", "The benchmark runs again. The new memory can influence the answer, but only after ERINYS governance."),
    Segment(VIDEO_DIR / "build" / "app-tour-public-v2" / "10-saved-decisions.png", "The Memory Decisions panel is the proof. Current care is selected. Stale routines are demoted. Private identifiers are blocked."),
    Segment(VIDEO_DIR / "erinys-caredog-proof.png", "This is the outcome. Three synthetic private IDs are blocked, and zero private IDs leak into the governed answer. The win is governance, not token trimming.", pause=1.0),
    Segment(VIDEO_DIR / "erinys-caredog-architecture-clean.png", "The architecture is simple. Candidate memories enter ERINYS. Governance rules filter them. Only selected memory becomes Qwen prompt context."),
    Segment(VIDEO_DIR / "erinys-caredog-closing.png", "For family health care, the value is not remembering everything. ERINYS governs memory. Qwen generates the answer. Memory quality is a decision layer.", pause=1.4),
    Segment(VIDEO_DIR / "erinys-caredog-cta.png", "You can find Ghosty.AI on GitHub at GhostyAI H A, visit aionexo dot com, and read the Alibaba Cloud blog post, From Agents to Directors.", pause=3.2),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT.parents[2] / ".env")
    parser.add_argument("--voice-id", default=VOICE_ID)
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def run_command(cmd: list[str]) -> None:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-4000:])


def ffprobe_duration(path: Path) -> float:
    output = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        text=True,
    )
    return float(output.strip())


def generate_audio(segment: Segment, index: int, args: argparse.Namespace) -> Path:
    cache_key = audio_cache_key(segment.text, args.model_id, args.voice_id)
    output = BUILD_DIR / "raw-audio" / f"segment_{index:02d}_{cache_key}.mp3"
    if output.exists() and not args.force:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = build_payload(segment.text, args.model_id)
    output.write_bytes(request_bytes(speech_url(args.voice_id), require_api_key(), payload))
    return output


def generate_narration_audio(args: argparse.Namespace) -> Path:
    text = build_narration_text()
    cache_key = audio_cache_key(text, args.model_id, args.voice_id)
    output = BUILD_DIR / "raw-audio" / f"continuous_{cache_key}.mp3"
    if output.exists() and not args.force:
        return output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(request_bytes(speech_url(args.voice_id), require_api_key(), build_payload(text, args.model_id)))
    return output


def build_narration_text() -> str:
    return "\n\n".join(segment.text for segment in SEGMENTS)


def audio_cache_key(text: str, model_id: str, voice_id: str) -> str:
    content = f"{voice_id}\n{model_id}\n{text}".encode("utf-8")
    return hashlib.sha256(content).hexdigest()[:12]


def estimate_segment_seconds(segment: Segment) -> float:
    spoken = len(segment.text.split()) / TARGET_WPM * 60
    return max(spoken + segment.pause, 2.8)


def create_video_segment(image_path: Path, output: Path, duration: float) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    video_filter = video_segment_filter(duration)
    run_command([
        "ffmpeg", "-y", "-loop", "1", "-framerate", FPS, "-t", f"{duration:.3f}",
        "-i", str(image_path), "-vf", video_filter, "-map", "0:v:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        str(output),
    ])


def video_segment_filter(duration: float) -> str:
    fade_out_start = max(duration - 0.18, 0)
    return (
        f"scale={FRAME_WIDTH}:{FRAME_HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={FRAME_WIDTH}:{FRAME_HEIGHT},setsar=1,fps={FPS},"
        f"fade=t=in:st=0:d=0.12,fade=t=out:st={fade_out_start:.3f}:d=0.18"
    )


def write_concat_list(paths: list[Path], output: Path) -> Path:
    output.write_text("\n".join(f"file '{path.resolve()}'" for path in paths) + "\n", encoding="utf-8")
    return output


def concat_segments(segment_paths: list[Path], output: Path) -> None:
    concat_list = write_concat_list(segment_paths, BUILD_DIR / "segments.txt")
    run_command([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        str(output),
    ])


def normalize_audio_video(input_video: Path, input_audio: Path, output_video: Path, duration: float) -> None:
    audio_filter = (
        f"[1:a]aresample=48000,aformat=channel_layouts=mono,"
        f"apad,atrim=0:{duration:.3f},loudnorm=I=-16:LRA=11:TP=-1.5[a]"
    )
    run_command([
        "ffmpeg", "-y", "-i", str(input_video), "-i", str(input_audio),
        "-filter_complex", audio_filter, "-map", "0:v:0", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart", str(output_video),
    ])


def format_srt_time(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def format_vtt_time(seconds: float) -> str:
    return format_srt_time(seconds).replace(",", ".")


def create_cues(durations: list[float]) -> list[CaptionCue]:
    cues: list[CaptionCue] = []
    cursor = 0.0
    for index, (segment, duration) in enumerate(zip(SEGMENTS, durations, strict=True), start=1):
        cues.append(CaptionCue(index=index, start=cursor, end=cursor + duration, text=segment.text))
        cursor += duration
    return cues


def write_srt(cues: list[CaptionCue], path: Path) -> None:
    blocks = [srt_block(cue) for cue in cues]
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


def srt_block(cue: CaptionCue) -> str:
    return f"{cue.index}\n{format_srt_time(cue.start)} --> {format_srt_time(cue.end)}\n{cue.text}"


def write_vtt(cues: list[CaptionCue], path: Path) -> None:
    blocks = [vtt_block(cue) for cue in cues]
    path.write_text("WEBVTT\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")


def vtt_block(cue: CaptionCue) -> str:
    return f"{cue.index}\n{format_vtt_time(cue.start)} --> {format_vtt_time(cue.end)}\n{cue.text}"


def scale_durations(audio_duration: float) -> list[float]:
    weights = [estimate_segment_seconds(segment) for segment in SEGMENTS]
    target = audio_duration + END_HOLD_SECONDS
    scale = target / sum(weights)
    return [round(weight * scale, 3) for weight in weights]


def build_segments(durations: list[float]) -> list[Path]:
    video_paths: list[Path] = []
    for index, (segment, duration) in enumerate(zip(SEGMENTS, durations, strict=True), start=1):
        video_mp4 = BUILD_DIR / "video" / f"segment_{index:02d}.mp4"
        create_video_segment(segment.image, video_mp4, duration)
        video_paths.append(video_mp4)
    return video_paths


def main() -> int:
    args = parse_args()
    load_env_file(args.env_file)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    audio = generate_narration_audio(args)
    durations = scale_durations(ffprobe_duration(audio))
    video_paths = build_segments(durations)
    draft = BUILD_DIR / "erinys-caredog-demo-audio-driven-draft.mp4"
    concat_segments(video_paths, draft)
    output = BUILD_DIR / "erinys-caredog-demo-audio-driven.mp4"
    normalize_audio_video(draft, audio, output, sum(durations))
    cues = create_cues(durations)
    write_srt(cues, VIDEO_DIR / "erinys-caredog-youtube-captions.srt")
    write_vtt(cues, VIDEO_DIR / "erinys-caredog-youtube-captions.vtt")
    FINAL_VIDEO.write_bytes(output.read_bytes())
    print(f"wrote={FINAL_VIDEO}")
    print(f"duration={sum(durations):.3f}")
    print("voice=Bella")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
