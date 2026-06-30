# Alibaba Cloud Function Compute Deployment

Recommended submission shape: deploy one custom container that serves both the
React frontend and the FastAPI backend. Judges get one public URL, and the app
calls `/health`, `/memories`, `/run/governance`, and `/run/benchmark` on the same
origin.

## Container Image

Build from the project root:

```bash
docker build -f Dockerfile.alibaba -t erinys-care-memory-alibaba:latest .
```

Local smoke run:

```bash
docker run --rm -p 8000:8000 \
  --env-file deploy/alibaba-function-compute/env.example \
  -e QWEN_API_KEY=<your Qwen Cloud or DashScope key> \
  erinys-care-memory-alibaba:latest
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
```

## Alibaba Cloud Setup

Push the image to Alibaba Cloud Container Registry, then create a Function
Compute custom-container function from that image.

Use these Function Compute settings:

```text
Runtime: custom container
Trigger: HTTP
Container listen port: 8000
Request timeout: 120 seconds
Memory: 1 GB or higher
CPU: 1 vCPU or higher
```

If the service injects a `PORT` environment variable, the container uses it.
Otherwise it listens on `8000`.

## Required Environment Variables

Set these in Function Compute. Never bake secrets into the image.

```bash
QWEN_API_KEY=<your Qwen Cloud or DashScope key>
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.7-plus
ERINYS_USE_MOCK_QWEN=false
ERINYS_DEMO_SEED=/app/data/demo/care_memory.seed.json
ERINYS_MEMORY_STORE=/tmp/runtime_memory.json
ERINYS_WEB_DIST=/app/web/dist
ERINYS_ALLOWED_ORIGINS=
PORT=8000
```

`ERINYS_ALLOWED_ORIGINS` can stay empty for the one-container deployment because
the frontend and API are served from the same origin. Set it only if the
frontend is hosted separately.

## Health Check

After deployment:

```bash
curl https://<function-url>/health
```

Expected live response shape:

```json
{
  "status": "ok",
  "qwen": {
    "provider": "qwen-cloud",
    "mode": "live",
    "api_key_configured": true
  },
  "erinys": {
    "provider": "erinys",
    "runtime": "erinys-policy-runtime"
  }
}
```

Run the deployment smoke test:

```bash
python deploy/alibaba-function-compute/smoke_test.py https://<function-url>
```

The smoke test validates `/health` and `/run/benchmark`, including the three
benchmark modes.

## Separate Frontend Option

If you still want to host the React build separately, build it with the backend
function URL:

```bash
cd web
VITE_API_BASE_URL=https://<function-url> npm run build
```

Upload `web/dist/` to the static host and set `ERINYS_ALLOWED_ORIGINS` on the
backend to the exact frontend origin. Do not use `*` for the public submission.

## Devpost Live Demo URL

Submit the Function Compute public URL as the live demo. The page should show:

1. `Qwen Cloud live`.
2. A save-memory control.
3. Three answer modes: No Memory, Raw Memory, ERINYS + Qwen.
4. Memory Decisions with selected, conflicted, demoted, and blocked memories.
