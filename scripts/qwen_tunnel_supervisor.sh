#!/usr/bin/env bash
set -u

ACTION="${1:-start}"
PROJECT_DIR="${CM_PROJECT_DIR:-/home/jovyan/work/causal-mind-v2}"
SETUP_DIR="${QWEN_SETUP_DIR:-$PROJECT_DIR/.qwen-setup}"
RUNAI_BIN="${RUNAI_BIN:-$PROJECT_DIR/.runai-cli/bin/runai}"
PID_FILE="$SETUP_DIR/supervisor.pid"
FORWARD_PID_FILE="$SETUP_DIR/port-forward.pid"
LOG_DIR="$SETUP_DIR/logs"
MODEL_ID="Qwen/Qwen3.8-27B-FP8"
BASE_URL="http://127.0.0.1:18000/v1"
WORKSPACE="${QWEN_WORKSPACE:-qwen38-27b12}"
PROJECT_FLAG="${QWEN_PROJECT_FLAG:-romania-dev}"
REMOTE_PORT="${QWEN_REMOTE_PORT:-8000}"

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

auth_ok() {
  "$RUNAI_BIN" auth get-token -o plaintext >/dev/null 2>&1
}

start_forward() {
  if [ -f "$FORWARD_PID_FILE" ] && is_alive "$(cat "$FORWARD_PID_FILE")"; then
    return 0
  fi
  "$RUNAI_BIN" \
    workspace port-forward "$WORKSPACE" \
    -p "$PROJECT_FLAG" \
    --port 18000:"$REMOTE_PORT" \
    --address localhost \
    >>"$LOG_DIR/port-forward.log" 2>&1 &
  echo "$!" > "$FORWARD_PID_FILE"
}

run_loop() {
  echo "$$" > "$PID_FILE"
  trap 'stop_child "$FORWARD_PID_FILE"; rm -f "$PID_FILE"; exit 0' INT TERM EXIT

  local failures=0
  while true; do
    if ! auth_ok; then
      echo "$(date -Is) waiting for Run:ai authentication" >>"$LOG_DIR/supervisor.log"
      sleep 30
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
    sleep 10
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
