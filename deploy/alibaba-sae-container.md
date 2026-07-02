# Alibaba Cloud SAE Container Notes

Use this if you want a managed web app instead of managing an ECS instance.

## Shape

- Source image: `erinys-care-memory:latest` pushed to Alibaba Cloud Container Registry.
- Container port: `8000`.
- Public access: enabled.
- Health check path: `/health`.
- Environment variables:
  - `QWEN_API_KEY`
  - `QWEN_MODEL=qwen3.7-plus`
  - `QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
  - `QWEN_LIVE=1`
  - `ERINYS_APP_DATA_DIR=/data`

## Tradeoff

SAE is cleaner for a public demo URL, but runtime-added memories are ephemeral unless you attach persistent storage. For the hackathon demo, that is usually acceptable because the seeded ERINYS memory benchmark is built into the image.
