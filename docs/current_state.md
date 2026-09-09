# Current State

## Current stage

Phase 0/1: infrastructure validated, epistemic seal frozen, dataset audit starting.

## Validated results

- L0: Qwen endpoint `Qwen/Qwen3.8-27B-FP8` reachable at `http://127.0.0.1:18000/v1`
  (chat + tool calls), tunnel supervisor self-heals.
- L0: task queue claim locking, worktree isolation, agent harness smoke tests.

## Failed hypotheses

(none yet)

## Active tasks

- CM-1: authoritative audit of OpenNeuro ds006067 (metadata, subjects, runs, TR,
  transcripts, timestamps, annotations, license, footprint); minimal-subset download;
  manifest + checksums.
- CM-0: finalize epistemic seal docs; freeze split definitions once subject count known.
- Phase C: smoke-test all six agents with small independent tasks.

## Blockers

- **Contingency (not currently blocking):** Run:ai CLI token expires 2026-09-10;
  refresh token should auto-renew. If it does not, a human must run
  `runai login remote-browser` in the pod (exact steps in
  `docs/runbooks/qwen_tunnel.md`).

## Next gates

- GATE A (data integrity) after ds006067 subset lands and loader validates.
- GATE B (non-neural signal) after baseline battery.

## Key commit hashes

- (initial commit pending)

## Exact reproducibility commands

```bash
# on the pod
cd /home/jovyan/work/causal-mind
scripts/qwen_tunnel_supervisor.sh status
scripts/cm-uv run cm status
scripts/cm-uv run pytest
scripts/cm-uv run ruff check .
```
