#!/usr/bin/env bash
set -u

cd /home/jovyan/work/causal-mind-v2 || exit 1
mkdir -p orchestration/logs

PORT="${1:-18001}"
BASE="http://127.0.0.1:$PORT/v1"

cleanup() {
  [ -n "${pf_pid:-}" ] && kill "$pf_pid" 2>/dev/null || true
}
trap cleanup EXIT

# If the supervised endpoint is already healthy, just verify it.
if curl -fsS http://127.0.0.1:18000/v1/models 2>/dev/null | grep -F "Qwen/Qwen3.8-27B-FP8" >/dev/null; then
  echo "---MODELS (supervised endpoint)---"
  curl -fsS http://127.0.0.1:18000/v1/models || true
  echo
  exit 0
fi

echo "---starting temporary port-forward on $PORT---"
nohup .runai-cli/bin/runai \
  workspace port-forward qwen38-27b12 \
  -p romania-dev \
  --port "$PORT:8000" \
  --address localhost \
  > orchestration/logs/pf_proxy_test.log 2>&1 &
pf_pid=$!

sleep 15

echo "---MODELS---"
curl -fsS "$BASE/models" || true
echo
echo "---PFLOG---"
sed -n '1,100p' orchestration/logs/pf_proxy_test.log || true
