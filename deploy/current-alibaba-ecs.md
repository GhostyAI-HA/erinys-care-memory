# Current Alibaba ECS Deployment

Created for the Qwen Cloud hackathon demo on 2026-07-01.

## Public endpoints

- UI: `https://hack.aionexo.com/GAI-HS/`
- Health: `https://hack.aionexo.com/GAI-HS/health`
- Benchmark API: `https://hack.aionexo.com/GAI-HS/run/benchmark`
- Origin UI: `http://47.236.156.71/`

## Alibaba Cloud resources

- Region: `ap-southeast-1`
- Zone: `ap-southeast-1b`
- ECS instance: `i-t4n0rqg85x7q2c35sxhq`
- Instance name: `erinys-care-memory-20260701011905`
- Instance type: `ecs.t6-c1m1.large`
- Public IP: `47.236.156.71`
- VPC: `vpc-t4nt824htc9y9jn2ssbmj`
- VSwitch: `vsw-t4neyyb51l80viqpivkwf`
- Security group: `sg-t4ngcbi9da2goqiph2jb`
- Key pair: `erinys-care-key-20260701011905`

## Current status

- App container is running on public port `80`.
- Docker health check is configured.
- `/health` returns `ok: true`.
- `/run/benchmark` returns the three-way comparison.
- Qwen model is configured as `qwen3.7-plus`.
- Qwen live key is installed, so `qwen_live_configured` is currently `true`.
- Verified providers: `no_memory:qwen_cloud`, `raw_memory:qwen_cloud`, `erinys_qwen:qwen_cloud`.
- Governed-prompt token reduction: `~25%` vs raw memory (rough char/4 estimate, not a measured provider token count).

## Latest smoke test

Verified at `2026-07-02 00:20:37 JST`.

- Public `/health`: pass.
- Public HTML shell and static assets: pass.
- Hero CareDog image: pass, WebP `erinys-care-dog-hero-640.webp` loaded in the first viewport.
- Initial page load: pass, no `/run/benchmark` request before user action.
- Public first-view browser check: pass, with no page errors or failed requests.
- Governance API: pass, with private memory IDs `m008`, `m013`, and `m014` blocked.
- Runtime memory save, persistence, reset, and cleanup: pass.
- Public `/run/benchmark`: pass after pressing the demo run button.
- Qwen providers: `no_memory:qwen_cloud`, `raw_memory:qwen_cloud`, `erinys_qwen:qwen_cloud`.
- Qwen errors: none.
- Prompt-token reduction: `~25%` (rough char/4 estimate of the governed vs raw prompt).
- UI screenshots:
  - `/private/tmp/erinys-public-fast-start.png`
  - `/private/tmp/erinys-public-fast-after-save.png`

## Verify

```bash
curl -fsS https://hack.aionexo.com/GAI-HS/health
curl -fsS -X POST https://hack.aionexo.com/GAI-HS/run/benchmark \
  -H 'Content-Type: application/json' \
  -d '{}'
```

## SSH

```bash
ssh -i /tmp/erinys-care-memory-ecs-key \
  -o UserKnownHostsFile=/tmp/erinys-care-memory-known-hosts \
  root@47.236.156.71
```

## Install Qwen key

Do not paste the key into chat logs. SSH to the instance and edit:

```bash
cd /opt/erinys-care-memory
nano .env
docker restart erinys-care-memory
scripts/verify_service.sh http://127.0.0.1
```

Set:

```bash
QWEN_API_KEY=...
QWEN_MODEL=qwen3.7-plus
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
QWEN_LIVE=1
```

## Stop cost

Stop the instance:

```bash
aliyun ecs StopInstance \
  --RegionId ap-southeast-1 \
  --InstanceId i-t4n0rqg85x7q2c35sxhq
```

Release the instance after the demo:

```bash
aliyun ecs DeleteInstance \
  --RegionId ap-southeast-1 \
  --InstanceId i-t4n0rqg85x7q2c35sxhq \
  --Force true
```

After deleting the instance, clean up the network resources if no longer needed:

```bash
aliyun ecs DeleteSecurityGroup --RegionId ap-southeast-1 --SecurityGroupId sg-t4ngcbi9da2goqiph2jb
aliyun vpc DeleteVSwitch --RegionId ap-southeast-1 --VSwitchId vsw-t4neyyb51l80viqpivkwf
aliyun vpc DeleteVpc --RegionId ap-southeast-1 --VpcId vpc-t4nt824htc9y9jn2ssbmj
aliyun ecs DeleteKeyPairs --RegionId ap-southeast-1 --KeyPairNames '["erinys-care-key-20260701011905"]'
```
