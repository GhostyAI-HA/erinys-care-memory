# Track 1: ERINYS Care Memory

ERINYS Care Memory is a MemoryAgent that decides what Qwen should trust.

This repository is self-contained for judging. It includes a compact ERINYS
policy runtime that reproduces the memory-governance behavior used in the demo:
select current memories, demote stale memories, mark contradictions, block
private identifiers, and send only selected context to Qwen Cloud.

## Core Claim

Long-running assistants need more than storage. They need memory governance:

- recall critical context
- demote outdated routines
- detect contradictions
- block sensitive identifiers
- fit only the useful memories into the Qwen context window

## Three-Mode Demo

The same user request is run through three modes:

| Mode | Behavior |
| --- | --- |
| No Memory | Admits it cannot know exact timing, transport, or constraints without memory. |
| Raw Memory | Plausibly mixes stale routines, conflicts, and private identifiers. |
| ERINYS + Qwen | Uses only selected care context and explains memory decisions. |

## Local Backend

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m uvicorn erinys_qwen_agent.api:app --reload
```

## Run the Demo UI

With the backend running on port 8000, start the Vite dev server in a second
terminal:

```bash
cd web
npm install
npm run dev
```

Then open http://127.0.0.1:5173. The dev server proxies `/health`, `/memories`,
`/run/governance`, and `/run/benchmark` to the backend on `127.0.0.1:8000`.

## API Surface

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/memories
curl http://127.0.0.1:8000/run/governance
curl -X POST http://127.0.0.1:8000/memories \
  -H 'content-type: application/json' \
  -d '{"text":"Ask reception to arrange wheelchair assistance at the north entrance before check-in.","kind":"event","importance":5,"recency":5}'
```

`/health` exposes both the Qwen connection and the ERINYS policy runtime.
`/memories` shows seed memory plus locally persisted demo memory.
`/run/governance` returns every memory decision plus the selected memory IDs.

## Persistent Memory Proof

The demo is not only a fixed seed comparison. Reviewers can save a new memory,
rerun the same prompt, reload the app, and see the saved memory reused in the
ERINYS + Qwen answer.

Runtime memories are written to:

```text
data/demo/runtime_memory.json
```

That file is intentionally ignored by Git so local demo state and API keys do
not enter the public repository.

## Qwen Cloud Live Mode

By default the demo uses a deterministic mock so it is safe to run without credentials.
For the hackathon video, switch to live Qwen Cloud mode:

```bash
cp .env.example .env
```

Then edit `.env` locally:

```bash
QWEN_API_KEY=<your Qwen Cloud or DashScope API key>
ERINYS_USE_MOCK_QWEN=false
QWEN_MODEL=qwen3.7-plus
```

Restart the backend after editing `.env`. The `/health` endpoint should report:

```json
{"qwen":{"mode":"live","api_key_configured":true}}
```

Never commit `.env`. It is ignored by `.gitignore`.

Then call:

```bash
curl -X POST http://127.0.0.1:8000/run/benchmark \
  -H 'content-type: application/json' \
  -d '{"request":"Draft the exact door-to-door plan for tomorrow'\''s clinic visit using only what you remember. Include timing, transport, what to bring, questions to ask, and what not to expose. If you lack the memory, say what cannot be known instead of giving a generic checklist.","scenario":"care_visit"}'
```

## Verification

```bash
python -m pytest
python -m ruff check src tests
python -m compileall src
cd web && npm run build
```

## Submission Shape

Submit three artifacts together:

1. Demo video: show save-memory, three-way comparison, and memory decisions.
2. Interactive app URL: let judges save one synthetic memory and rerun the comparison.
3. Public GitHub repo: include source, tests, docs, and deployment notes.

For a public frontend build, point Vite at the deployed backend:

```bash
cd web
VITE_API_BASE_URL=https://<backend-url> npm run build
```

Set `ERINYS_ALLOWED_ORIGINS` on the backend to the deployed frontend origin.

## Alibaba Cloud Deployment

The recommended judge demo deployment is a single Alibaba Cloud Function Compute
custom container using `Dockerfile.alibaba`. It serves both the React frontend
and the FastAPI backend from one public URL, so judges can open the app and the
browser can call `/health`, `/memories`, `/run/governance`, and `/run/benchmark`
on the same origin.

```bash
docker build -f Dockerfile.alibaba -t erinys-care-memory-alibaba:latest .
```

For a backend-only container, use `Dockerfile.backend`.

See:

```text
deploy/alibaba-function-compute/README.md
```

The public repository should include `LICENSE` and must never include `.env`.
