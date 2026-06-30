# Alibaba Cloud / Qwen Cloud Proof

## What The Backend Uses

The backend calls Qwen Cloud through the OpenAI-compatible DashScope endpoint:

```text
https://dashscope-intl.aliyuncs.com/compatible-mode/v1
```

Implementation file:

```text
src/erinys_qwen_agent/qwen_adapter.py
```

The adapter reads:

- `QWEN_API_KEY` or `DASHSCOPE_API_KEY`
- `QWEN_BASE_URL`
- `QWEN_MODEL`
- `ERINYS_USE_MOCK_QWEN`

## Runtime Evidence

When live mode is configured, `/health` returns:

```json
{
  "qwen": {
    "provider": "qwen-cloud",
    "model": "qwen3.7-plus",
    "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "api_key_configured": true,
    "mock_requested": false,
    "mode": "live"
  },
  "erinys": {
    "provider": "erinys",
    "runtime": "erinys-policy-runtime",
    "version": "1.0.0"
  }
}
```

## Deployment Path

For the hosted submission, run the all-in-one custom container on Alibaba Cloud
Function Compute:

```bash
docker build -f Dockerfile.alibaba -t erinys-care-memory-alibaba:latest .
```

The container serves:

```text
/                    React frontend
/assets/*            Vite assets
/health              Qwen Cloud and ERINYS runtime status
/memories            seed plus persisted demo memory
/run/governance      memory decisions without generation
/run/benchmark       three-mode Qwen comparison
```

Required Alibaba Cloud Function Compute settings:

```text
Runtime: custom container
Trigger: HTTP
Container listen port: 8000
Environment: deploy/alibaba-function-compute/env.example values
```

After deployment, verify the public URL with:

```bash
python deploy/alibaba-function-compute/smoke_test.py https://<function-url>
```

The frontend can still be hosted separately, but the single-container deployment
is the preferred Devpost live demo because it avoids CORS and API URL mismatch.
