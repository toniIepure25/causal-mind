#!/usr/bin/env bash
set -euo pipefail

cd /home/jovyan/work/causal-mind
mkdir -p orchestration/logs

scripts/qwen_tunnel_supervisor.sh status

for n in 1 2 3; do
  echo "---OPENCODE-$n---"
  timeout 180 scripts/opencode-run-pty \
    --pure \
    --thinking \
    --format json \
    --agent smoke \
    -m runai/qwen38-27b12 \
    "Do not use tools. Think briefly and answer exactly TEST-$n." \
    > "orchestration/logs/opencode_pty_$n.jsonl"
  grep -q "TEST-$n" "orchestration/logs/opencode_pty_$n.jsonl"
  echo "opencode-$n-ok"
done
