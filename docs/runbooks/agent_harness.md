# Agent Harness Runbook

Autonomous workers use the direct Qwen tool loop (ADR-004).

## One worker, one task

```bash
cd /home/jovyan/work/causal-mind
scripts/qwen_tunnel_supervisor.sh status
scripts/cm-agent-once researcher          # claims one task, runs it, reports
```

## All six workers (supervisors)

```bash
scripts/cm-agent-supervisor start
scripts/cm-agent-supervisor status
scripts/cm-agent-supervisor stop
```

Each supervisor loops: claim next task for its worker -> run the agent tool loop in the
worker's worktree -> write report -> transition task to review -> sleep.

Worktrees: `/home/jovyan/work/worktrees/causal-mind/<worker>` (created by
`scripts/create_agent_worktrees.sh`).

## Queue controls

```bash
scripts/cm-uv run cm task list
scripts/cm-uv run cm task claim <worker>
scripts/cm-uv run cm task review <task-id>
scripts/cm-uv run cm task done <task-id>
scripts/cm-uv run cm task blocked <task-id>
scripts/cm-uv run cm task killed <task-id>
scripts/cm-uv run cm status
```

Claiming is atomic (file rename); a task is never claimed twice. Tasks with
unsatisfied dependencies (not in `done/`) are skipped.

## Environment variables

| var | default | meaning |
| --- | --- | --- |
| `CM_QUEUE_ROOT` | `<repo>/orchestration/tasks` | central task queue |
| `CM_REPORT_ROOT` | `<repo>/reports` | central report inbox |
| `CM_WORKTREE_ROOT` | `/home/jovyan/work/worktrees/causal-mind` | worktree root |
| `CM_QWEN_BASE_URL` | `http://127.0.0.1:18000/v1` | Qwen endpoint |
| `CM_QWEN_MODEL` | `Qwen/Qwen3.8-27B-FP8` | model id |
| `CM_AGENT_MAX_CYCLES` | `40` | tool-loop guard |
| `CM_AGENT_SLEEP_SECONDS` | `60` | idle sleep between claims |

When running from per-worker worktrees, always point `CM_QUEUE_ROOT` and
`CM_REPORT_ROOT` at the base repo so all agents share one queue and one report inbox.

## Concurrency policy

Start with 1-2 concurrent workers. Probe the endpoint with
`scripts/test_qwen_concurrency.sh 1 2 4 6` and only scale to six concurrent workers if
latency and error rate stay acceptable. The single A100 is shared with experiments;
GPU work and agent loops must not fight for the device (agents are CPU-bound; GPU
experiments get the device).
