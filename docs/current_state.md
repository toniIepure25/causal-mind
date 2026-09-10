# Current State

## Current stage

Phase 1: infrastructure validated, all six agents smoke-tested, epistemic seal frozen,
dataset audit starting.

## Validated results

- L0: Qwen endpoint `Qwen/Qwen3.8-27B-FP8` reachable at `http://127.0.0.1:18000/v1`
  (chat + tool calls); tunnel supervisor self-heals (direct port-forward, no Caddy).
- L0: task queue claim locking, worktree isolation, agent harness.
- L0: all six agents (orchestrator, researcher, data, forecasting, causal, reviewer)
  completed independent smoke tasks end-to-end (SMOKE-*-001, all reviewed and done).

## Failed hypotheses

(none yet)

## Active tasks

- CM-1: authoritative audit of OpenNeuro ds006067 (metadata, subjects, runs, TR,
  transcripts, timestamps, annotations, license, footprint); minimal-subset download;
  manifest + checksums.
- CM-0: finalize epistemic seal docs; freeze split definitions once subject count known.

## Blockers

- **Token lifecycle:** Run:ai CLI tokens expire ~daily; refresh tokens do NOT auto-renew
  in the CLI. When the token expires, a human must complete
  `runai login remote-browser` (open URL, paste code). Runbook:
  `docs/runbooks/qwen_tunnel.md`. The pod-side helper
  `scripts/runai_login_pty.py` stages the flow and waits for the code in
  `/tmp/runai-code.txt`.

## Next gates

- GATE A (data integrity) after ds006067 subset lands and loader validates.
- GATE B (non-neural signal) after baseline battery.

## Key commit hashes

- `307770b` rebuild at jovyan-owned root + smoke results
- `807e458` scripts pointed at v2 root, safe.directory for git-on-NFS

## Exact reproducibility commands

```bash
# on the pod, via SSH as jovyan (sidecar netns)
cd /home/jovyan/work/causal-mind-v2
scripts/qwen_tunnel_supervisor.sh status
.venv/bin/python -m causal_mind.cli status
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
```

## Environment notes

- Working root: `/home/jovyan/work/causal-mind-v2` (jovyan-owned). The original
  `/home/jovyan/work/causal-mind` is a frozen root-owned snapshot (NFS ownership split).
- Worktrees: `/home/jovyan/work/worktrees/causal-mind-v2/<worker>`.
- All git commands need `safe.directory=*` (NFS maps ownership to uid 65534);
  scripts and the planner set this automatically.
- The SSH session runs in a sidecar network namespace: the main container's
  127.0.0.1:18000 is NOT visible there. The tunnel supervisor binds the port-forward
  inside the SSH netns; the cluster gateway is reachable directly via
  `cisco-ai-pod.cc-demos.com` (no Caddy needed).
