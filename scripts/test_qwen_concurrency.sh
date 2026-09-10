#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:18000/v1"
MODEL_ID="Qwen/Qwen3.8-27B-FP8"

run_one() {
    local n="$1"
    curl -fsS \
      -H "Content-Type: application/json" \
      -d "{\"model\":\"$MODEL_ID\",\"messages\":[{\"role\":\"user\",\"content\":\"Reply exactly OK-$n\"}],\"max_tokens\":64,\"stream\":false}" \
      "$BASE_URL/chat/completions" >/tmp/qwen_conc_"$n".json
    echo "req-$n-ok"
}

export -f run_one
export BASE_URL MODEL_ID

parallelisms=("$@")
if [ "$#" -eq 0 ]; then
    parallelisms=(1 2 4)
fi

for parallelism in "${parallelisms[@]}"; do
    echo "---CONCURRENCY-$parallelism---"
    seq 1 "$parallelism" | xargs -I{} -P "$parallelism" bash -lc 'run_one "$@"' _ {}
done
