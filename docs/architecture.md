# Architecture

```text
React demo UI
  -> FastAPI backend
    -> ERINYS policy runtime
      -> selected memory context
    -> Qwen Cloud OpenAI-compatible API
      -> final answer
```

## Components

- Synthetic memory seed: safe demo memories only.
- ERINYS policy runtime: selected, ignored, demoted, contradiction, blocked.
- Qwen adapter: DashScope/Qwen OpenAI-compatible endpoint.
- Demo UI: compares No Memory, Raw Memory, and ERINYS + Qwen.

## Runtime Contract

The hackathon repository is self-contained. `/health` returns the Qwen status
and the ERINYS policy runtime status:

```json
{
  "qwen": {"provider": "qwen-cloud", "mode": "live"},
  "erinys": {
    "provider": "erinys",
    "runtime": "erinys-policy-runtime",
    "policy": "select-current-block-private-demote-stale"
  }
}
```

`/run/governance` returns the full decision list and selected memory IDs so the
governance layer can be inspected without calling Qwen.

## Alibaba Cloud Deployment

The backend can be deployed to Alibaba Cloud Function Compute as a custom
container using `Dockerfile.backend`.

Deployment notes:

```text
deploy/alibaba-function-compute/README.md
```
