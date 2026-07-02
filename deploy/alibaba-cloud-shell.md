# Alibaba Cloud Shell Smoke Test Runbook

Cloud Shell is not the deployment target. It is a temporary smoke-test surface only.

Use `deploy/alibaba-ecs-docker.md` for the stable Alibaba Cloud run path.

## 1. Set Qwen Cloud securely

In Cloud Shell:

```bash
read -s QWEN_API_KEY
export QWEN_API_KEY
export QWEN_MODEL=qwen3.7-plus
export QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

If no key is set, the app still runs with deterministic fallback:

```bash
export QWEN_LIVE=0
```

## 2. Run

```bash
cd ~/erinys-care-memory
chmod +x scripts/cloudshell_run.sh
scripts/cloudshell_run.sh
```

## 3. Verify

```bash
curl -s http://127.0.0.1:8000/health
curl -s -X POST http://127.0.0.1:8000/run/benchmark \
  -H 'Content-Type: application/json' \
  -d '{}'
```

If Cloud Shell preview is unavailable, do not fight it. Verify with `curl` and move to ECS/SAE.

## 4. Judge-facing proof points

- The service runs on Alibaba Cloud infrastructure.
- The Qwen Cloud base URL is `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`.
- `/health` shows `model=qwen3.7-plus`.
- `/run/benchmark` shows No Memory vs Raw Memory vs ERINYS + Qwen.
- ERINYS blocks private identifiers before the governed prompt reaches Qwen.
