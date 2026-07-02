# Alibaba Cloud ECS Docker Runbook

This is the stable deployment path. Do not use Cloud Shell as the hosting surface; Cloud Shell is temporary and its VM is destroyed after the session expires.

## Target

- Alibaba Cloud ECS instance with a public IP.
- Security group inbound rule: TCP `80` from the judge/test IP range, or `0.0.0.0/0` for a temporary public demo.
- Docker container runs the app on internal port `8000` and publishes public port `80`.
- Qwen Cloud is configured through environment variables, not hard-coded files.

## 1. Build a release bundle locally

```bash
cd aionexo/project/erinys-care-memory
chmod +x scripts/*.sh
scripts/release_bundle.sh
```

Copy the printed `.tgz` file to the ECS instance:

```bash
scp /tmp/erinys-care-memory-release.tgz root@YOUR_ECS_PUBLIC_IP:/tmp/
```

## 2. Prepare the ECS instance

```bash
ssh root@YOUR_ECS_PUBLIC_IP
mkdir -p /opt/erinys-care-memory
tar -xzf /tmp/erinys-care-memory-release.tgz -C /opt/erinys-care-memory
cd /opt/erinys-care-memory
chmod +x scripts/*.sh
scripts/ecs_install_docker.sh
cp .env.example .env
chmod 600 .env
```

Edit `.env` on the ECS instance and set the Qwen Cloud key:

```bash
nano .env
```

Required values:

```bash
QWEN_API_KEY=YOUR_QWEN_KEY
QWEN_MODEL=qwen3.7-plus
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_LIVE=1
ERINYS_APP_DATA_DIR=/data
```

## 3. Run

```bash
cd /opt/erinys-care-memory
scripts/run_docker.sh .env
```

## 4. Verify

From the ECS instance:

```bash
scripts/verify_service.sh http://127.0.0.1
```

From your local machine:

```bash
curl -fsS http://YOUR_ECS_PUBLIC_IP/health
curl -fsS -X POST http://YOUR_ECS_PUBLIC_IP/run/benchmark \
  -H 'Content-Type: application/json' \
  -d '{}'
```

The important proof points:

- `/health` returns `"ok": true`.
- `/health` returns `"model": "qwen3.7-plus"`.
- `/health` returns `"qwen_live_configured": true` when the key is set.
- `/run/benchmark` returns three runs: `no_memory`, `raw_memory`, `erinys_qwen`.
- `erinys_qwen` blocks private identifiers before the prompt reaches Qwen.

## 5. Operations

Restart:

```bash
docker restart erinys-care-memory
```

Logs:

```bash
docker logs --tail 100 erinys-care-memory
```

Stop:

```bash
docker rm -f erinys-care-memory
```

Update:

```bash
tar -xzf /tmp/erinys-care-memory-release.tgz -C /opt/erinys-care-memory
cd /opt/erinys-care-memory
scripts/run_docker.sh .env
```
