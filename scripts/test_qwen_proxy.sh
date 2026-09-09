#!/usr/bin/env bash
set -u

cd /home/jovyan/work/causal-mind || exit 1
mkdir -p orchestration/logs

ps -u jovyan -o pid,args \
  | awk '/[C]addyfile.runai|[w]orkspace port-forward qwen38-27b12/{print $1}' \
  | xargs -r kill 2>/dev/null || true

nohup .caddy/bin/caddy run \
  --config /home/jovyan/.runai-proxy/Caddyfile.runai \
  --adapter caddyfile \
  > orchestration/logs/caddy_test.log 2>&1 &
caddy_pid=$!

sleep 2

nohup .runai-cli/bin/runai \
  --config-path /home/jovyan/.runai-proxy \
  --config-file config.json \
  workspace port-forward qwen38-27b12 \
  -p romania-dev \
  --port 18000:8000 \
  --address localhost \
  > orchestration/logs/pf_proxy_test.log 2>&1 &
pf_pid=$!

sleep 12

echo "---MODELS---"
curl -fsS http://127.0.0.1:18000/v1/models || true
echo
echo "---PFLOG---"
sed -n '1,100p' orchestration/logs/pf_proxy_test.log || true
echo "---CADDYLOG---"
sed -n '1,80p' orchestration/logs/caddy_test.log || true

kill "$pf_pid" 2>/dev/null || true
kill "$caddy_pid" 2>/dev/null || true
