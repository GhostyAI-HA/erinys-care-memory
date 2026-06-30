# Submission Checklist

## Required Assets

- [x] Public source code structure prepared.
- [x] MIT `LICENSE` file added.
- [x] `.gitignore` blocks `.env`, `.venv`, caches, and build output.
- [x] Qwen Cloud live integration implemented.
- [x] ERINYS policy runtime exposed through `/health`.
- [x] Persistent memory endpoint exposed through `/memories` and `POST /memories`.
- [x] Governance-only endpoint exposed through `/run/governance`.
- [x] Architecture diagram included at `docs/architecture.svg`.
- [x] Devpost copy drafted at `docs/devpost_submission.md`.
- [x] Three-minute demo script drafted at `docs/video_script.md`.
- [x] Presentation deck generated at `docs/presentation/erinys-care-memory-pitch.pptx`.
- [x] Alibaba/Qwen Cloud proof notes included at `docs/alibaba_cloud_proof.md`.
- [x] Alibaba Function Compute container deployment notes included at `deploy/alibaba-function-compute/README.md`.
- [x] Frontend supports `VITE_API_BASE_URL` for a public backend.
- [x] Backend supports `ERINYS_ALLOWED_ORIGINS` for a public frontend.

## Verification

- [x] `python -m pytest` passes.
- [x] `python -m ruff check src tests` passes.
- [x] `python -m compileall src` passes.
- [x] `npm run build` passes.
- [x] Live UI shows Qwen Cloud live mode.
- [x] Live UI shows ERINYS runtime.
- [x] Live UI shows saved persistent memory count.
- [x] Live UI shows No Memory gap, Raw Memory leak, and Governed exact plan.

## Manual Items Before Devpost Submit

- [ ] Create or choose the public GitHub repository.
- [ ] Push this project without `.env`, `.venv`, caches, or `web/node_modules`.
- [ ] Record and upload the 3-minute demo video.
- [ ] Deploy backend with Qwen API key stored server-side.
- [ ] Deploy frontend with `VITE_API_BASE_URL` pointing at backend.
- [ ] Verify public app can save memory and rerun comparison.
- [ ] Add the public repository URL to Devpost.
- [ ] Add the demo video URL to Devpost.
- [ ] Add the live deployment URL to Devpost.
- [ ] Add Alibaba Cloud proof screenshot if available.
- [ ] Upload the presentation deck.
