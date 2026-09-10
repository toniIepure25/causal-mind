# ADR-004: Agent harness — direct Qwen tool loop

Status: accepted (2026-09-09)

## Context

Two mechanisms are available for autonomous workers:

1. **OpenCode `run`** (PTY via `script`): proven for smoke tests, but the prior lab
   documented the non-TTY tool-loop path as fragile for long-running workers.
2. **Direct Qwen API tool loop**: a custom Python harness calling
   `http://127.0.0.1:18000/v1/chat/completions` with OpenAI-style function calling.
   Qwen3.8-27B-FP8 tool calling was verified working (hotc `test_qwen_tool_api.py`).

## Decision

Autonomous workers use the **direct Qwen tool loop** (`causal_mind.agent`):

- Tools: `bash` (jailed to the worker worktree, deny rules for push/rm -rf/credentials/
  kubectl), `read`, `write`, `edit`, `grep`, `glob`.
- Loop guards: max action cycles (default 40), repeated-command detection (same command
  3x in a row -> stop), no-progress detection (no file change / no new observation for
  N cycles -> stop), context safeguard (message budget; oldest tool outputs truncated),
  retry with exponential backoff on endpoint errors.
- Every run writes a structured report (decision, evidence, files changed, commands
  run, stop reason) to `reports/agents/<worker>/<task-id>.md` and updates task state.
- OpenCode remains available for interactive/TUI work (`.opencode/opencode.jsonc`).

## Consequences

- The harness is testable in isolation (mock client) — see `tests/test_agent_loop.py`.
- Concurrency starts at 1-2 workers; scale to 6 only after endpoint latency/stability
  is measured (see `scripts/test_qwen_concurrency.sh`).
