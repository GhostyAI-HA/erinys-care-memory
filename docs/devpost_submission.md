# Devpost Submission Draft

## Project Name

ERINYS Care Memory

## One-Liner

A Qwen Cloud MemoryAgent that decides which memories to trust, which to ignore, and which to block before generating an answer.

## Track

Track 1: MemoryAgent

## Project Description

ERINYS Care Memory demonstrates why long-running AI assistants need memory governance, not just memory storage.

The app sends the same caregiver request through three strategies:

1. No Memory: Qwen is careful, but cannot know exact appointment details.
2. Raw Memory: every retrieved memory is appended, so stale routines, contradictions, and private identifiers can leak into the plan.
3. ERINYS + Qwen: the ERINYS policy runtime selects current care memories, demotes stale ones, marks contradictions, blocks private identifiers, and sends only the selected context to Qwen Cloud.

The result is a safer, more specific answer with 64% fewer prompt tokens than the raw-memory baseline.

The latest build also includes a persistent memory proof: a reviewer can save a
new caregiver note, rerun the same prompt, reload the app, and see that saved
memory reused by the governed Qwen answer.

## What It Does

- Runs a same-prompt answer comparison across No Memory, Raw Memory, and ERINYS + Qwen.
- Saves new demo memories to a local persistent store and reuses them after reload.
- Shows judge-visible memory decisions: selected, ignored, demoted, contradiction, and blocked.
- Provides a governance-only API endpoint so reviewers can inspect memory decisions without calling Qwen.
- Exposes `/memories` and `POST /memories` so the persistence path is auditable.
- Uses Qwen Cloud live mode through the OpenAI-compatible DashScope endpoint.
- Keeps all demo memories synthetic and safe for public review.

The submitted demo is designed to be both watchable and touchable: the video
shows the full narrative in about three minutes, while the live app lets judges
save one synthetic memory and rerun the comparison themselves.

## How We Built It

- Frontend: React + TypeScript + Vite.
- Backend: FastAPI + Pydantic.
- AI: Qwen Cloud OpenAI-compatible API.
- Memory governance: a compact ERINYS policy runtime bundled in the repo for reproducible judging.
- Validation: pytest, ruff, Python compile checks, TypeScript build, and live browser verification.

## Qwen Cloud / Alibaba Cloud Usage

The backend calls Qwen Cloud through the OpenAI-compatible DashScope endpoint:

```text
https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

The implementation is in:

```text
src/erinys_qwen_agent/qwen_adapter.py
```

The `/health` endpoint reports whether Qwen is running in mock or live mode and exposes the model name used for the demo.

## What Makes It Different

The demo does not make the raw-memory baseline artificially bad. It shows a plausible RAG failure: retrieved memories are treated as useful context even when some are stale, contradictory, or private.

The winning moment is that Qwen is already smart, but it still cannot govern memory freshness, contradiction, and privacy by itself. ERINYS supplies that missing layer.

## Challenges

- Making the difference between No Memory and Governed Memory obvious without making No Memory look dumb.
- Showing a realistic Raw Memory failure without using real private data.
- Keeping the demo small enough to judge quickly while still exposing auditable memory decisions.

## Accomplishments

- Qwen Cloud live integration works.
- Persistent memory add/reload works in the demo app and backend tests.
- ERINYS governance decisions are visible in both UI and API.
- The governed answer keeps exact current details while blocking synthetic private identifiers.
- The final test suite validates the judge-facing contrast, not just implementation mechanics.

## What's Next

- Replace the compact bundled policy runtime with the full ERINYS memory stack for persistent multi-user memory.
- Add user-managed memory editing and redaction workflows.
- Deploy the backend to Alibaba Cloud Function Compute for the public demo endpoint.

## Links To Fill At Devpost Submission Time

- Public repository: add after the repo is published.
- Demo video: add after recording and uploading the video.
- Live deployment: add the deployed frontend URL after backend and frontend are connected.
- Architecture diagram: `docs/architecture.svg`
- Presentation: `docs/presentation/erinys-care-memory-pitch.pptx`
