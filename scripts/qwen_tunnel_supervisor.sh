#!/usr/bin/env bash
set -u

ACTION="${1:-start}"
SETUP_DIR="${QWEN_SETUP_DIR:-/home/jovyan/.qwen-runai-opencode}"
PROJECT_DIR="${CM_PROJECT_DIR:-/home/jovyan/work/causal-mind}"
RUNAI_BIN="${RUNAI_BIN:-$PROJECT_DIR/.runai-cli/bin/runai}"
CADDY_BIN="${CADDY_BIN:-$PROJECT_DIR/.caddy/bin/caddy}"
RUNAI_PROXY_DIR="${RUNAI_PROXY_DIR:-/home/jovyan/.runai-proxy}"
CADDYFILE="$RUNAI_PROXY_DIR/Caddyfile.runai"
PID_FILE="$SETUP_DIR/supervisor.pid"
FORWARD_PID_FILE="$SETUP_DIR/port-forward.pid"
CADDY_PID_FILE="$SETUP_DIR/caddy.pid"
LOG_DIR="$SETUP_DIR/logs"
MODEL_ID="Qwen/Qwen3.8-27B-FP8"
BASE_URL="http://127.0.0.1:18000/v1"

mkdir -p "$LOG_DIR"
chmod 700 "$SETUP_DIR"

is_alive() {
  local pid="${1:-}"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

stop_child() {
  local file="$1"
  if [ -f "$file" ]; then
    local pid
    pid="$(cat "$file" 2>/dev/null || true)"
    if is_alive "$pid"; then
      kill "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
    fi
    rm -f "$file"
  fi
}

health() {
  curl -fsS "$BASE_URL/models" 2>/dev/null | grep -F "$MODEL_ID" >/dev/null 2>&1
}

ensure_proxy_config() {
  mkdir -p "$RUNAI_PROXY_DIR"
  chmod 700 "$RUNAI_PROXY_DIR"
  if [ ! -f "$RUNAI_PROXY_DIR/authentication.json" ] && [ -f /home/jovyan/.runai/authentication.json ]; then
    cp /home/jovyan/.runai/authentication.json "$RUNAI_PROXY_DIR/authentication.json"
    chmod 600 "$RUNAI_PROXY_DIR/authentication.json"
  fi
  python3 - <<'PY'
from pathlib import Path
import json

base = Path("/home/jovyan/.runai/config.json")
out = Path("/home/jovyan/.runai-proxy/config.json")
data = json.loads(base.read_text())
data.setdefault("authentication", {})["file"] = "authentication.json"
data.setdefault("cluster", {})["domain"] = "http://127.0.0.1:19080"
out.write_text(json.dumps(data, indent=2) + "\n")
out.chmod(0o600)
PY
  cat > "$CADDYFILE" <<'EOF'
{
    admin off
    auto_https off
}

http://127.0.0.1:19080 {
    reverse_proxy https://10.130.240.221 {
        header_up Host cisco-ai-pod.cc-demos.com
        transport http {
            tls
            tls_server_name cisco-ai-pod.cc-demos.com
            tls_insecure_skip_verify
            dial_timeout 15s
            response_header_timeout 30s
        }
    }
}
EOF
  chmod 600 "$CADDYFILE"
}

start_caddy() {
  if [ -f "$CADDY_PID_FILE" ] && is_alive "$(cat "$CADDY_PID_FILE")"; then
    return 0
  fi
  "$CADDY_BIN" run --config "$CADDYFILE" --adapter caddyfile \
    >>"$LOG_DIR/caddy.log" 2>&1 &
  echo "$!" > "$CADDY_PID_FILE"
  sleep 2
}

start_forward() {
  if [ -f "$FORWARD_PID_FILE" ] && is_alive "$(cat "$FORWARD_PID_FILE")"; then
    return 0
  fi
  ensure_proxy_config
  start_caddy
  "$RUNAI_BIN" \
    --config-path "$RUNAI_PROXY_DIR" \
    --config-file config.json \
    workspace port-forward qwen38-27b12 \
    -p romania-dev \
    --port 18000:8000 \
    --address localhost \
    >>"$LOG_DIR/port-forward.log" 2>&1 &
  echo "$!" > "$FORWARD_PID_FILE"
}

run_loop() {
  echo "$$" > "$PID_FILE"
  trap 'stop_child "$FORWARD_PID_FILE"; stop_child "$CADDY_PID_FILE"; rm -f "$PID_FILE"; exit 0' INT TERM EXIT

  local failures=0
  while true; do
    ensure_proxy_config
    if ! "$RUNAI_BIN" --config-path "$RUNAI_PROXY_DIR" --config-file config.json auth get-token -o plaintext >/dev/null 2>&1; then
      echo "$(date -Is) waiting for Run:ai authentication" >>"$LOG_DIR/supervisor.log"
      sleep 15
      continue
    fi
    if ! health; then
      failures=$((failures + 1))
      if [ "$failures" -ge 2 ]; then
        echo "$(date -Is) restarting Qwen port-forward" >>"$LOG_DIR/supervisor.log"
        stop_child "$FORWARD_PID_FILE"
        start_forward
        failures=0
      else
        start_forward
      fi
    else
      failures=0
    fi
    sleep 5
  done
}

case "$ACTION" in
  start)
    if [ -f "$PID_FILE" ] && is_alive "$(cat "$PID_FILE")"; then
      echo "qwen tunnel supervisor already running: $(cat "$PID_FILE")"
      exit 0
    fi
    nohup "$0" run >"$LOG_DIR/supervisor.stdout.log" 2>"$LOG_DIR/supervisor.stderr.log" &
    echo "qwen tunnel supervisor started: $!"
    ;;
  run)
    run_loop
    ;;
  stop)
    stop_child "$FORWARD_PID_FILE"
    stop_child "$CADDY_PID_FILE"
    stop_child "$PID_FILE"
    ;;
  status)
    if [ -f "$PID_FILE" ] && is_alive "$(cat "$PID_FILE")"; then
      echo "RUNNING $(cat "$PID_FILE")"
    else
      echo "STOPPED"
    fi
    health && echo "QWEN HEALTHY" || echo "QWEN UNAVAILABLE"
    ;;
  *)
    echo "usage: $0 {start|run|stop|status}" >&2
    exit 2
    ;;
esac
