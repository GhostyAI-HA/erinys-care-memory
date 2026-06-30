# Submission Manifest

## Devpost Fields

- Project name: `ERINYS Care Memory`
- Track: `Track 1: MemoryAgent`
- Tagline: `A Qwen Cloud MemoryAgent that governs what memories should be trusted before generation.`
- Project description: use `docs/devpost_submission.md`.
- Demo video script: use `docs/video_script.md`.
- Presentation deck: `docs/presentation/erinys-care-memory-pitch.pptx`.
- Architecture diagram: `docs/architecture.svg`.
- Alibaba/Qwen proof: `docs/alibaba_cloud_proof.md`.
- Deployment notes: `deploy/alibaba-function-compute/README.md`.

## Code Entry Points

- Backend API: `src/erinys_qwen_agent/api.py`
- ERINYS policy runtime: `src/erinys_qwen_agent/memory_engine.py`
- Persistent memory store: `src/erinys_qwen_agent/memory_store.py`
- Qwen Cloud adapter: `src/erinys_qwen_agent/qwen_adapter.py`
- Demo seed: `data/demo/care_memory.seed.json`
- Frontend UI: `web/src/App.tsx`

## Public Repository Hygiene

Include:

- `README.md`
- `LICENSE`
- `.gitignore`
- `Dockerfile.backend`
- `src/`
- `tests/`
- `data/`
- `web/src/`
- `web/package.json`
- `web/package-lock.json`
- `web/tsconfig.json`
- `web/vite.config.ts`
- `docs/`
- `deploy/`

Do not include:

- `.env`
- `.venv/`
- `.pytest_cache/`
- `.ruff_cache/`
- `web/node_modules/`
- `web/dist/`
- `*.inspect.ndjson`
- `data/demo/runtime_memory.json`

## Final Verified State

- `pytest`: 14 passed.
- `ruff`: passed.
- `compileall`: passed.
- `npm run build`: passed.
- Persistent memory: `POST /memories` saved `u001`; governance selected it.
- Live UI: Qwen Cloud live, ERINYS Care Memory v1.0.0, 1 persisted memory, 63% fewer tokens.
- Architecture SVG: XML-valid and Chrome-rendered.
- Presentation deck: generated and visually checked.
