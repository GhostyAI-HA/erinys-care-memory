#!/usr/bin/env bash
set -euo pipefail

if command -v docker >/dev/null 2>&1; then
  docker --version
  exit 0
fi

SUDO=()
if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
  SUDO=(sudo)
fi

if command -v dnf >/dev/null 2>&1; then
  "${SUDO[@]}" dnf install -y docker
elif command -v yum >/dev/null 2>&1; then
  "${SUDO[@]}" yum install -y docker
elif command -v apt-get >/dev/null 2>&1; then
  "${SUDO[@]}" apt-get update
  "${SUDO[@]}" apt-get install -y docker.io
else
  echo "Install Docker manually, then rerun scripts/run_docker.sh." >&2
  exit 1
fi

"${SUDO[@]}" systemctl enable --now docker
docker --version
