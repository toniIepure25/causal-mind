# Research Log (chronological)

## 2026-09-09

- **Infrastructure audit.** Pod `orchestraiq-jupyter-5d6c688775-fbxj5` (namespace
  `runai-romania-dev`): A100-SXM4-40GB idle, 256-core node, ~1 TiB RAM, 107 TB free NFS
  at `/home/jovyan/work`, Python 3.13 (system) / 3.11 (uv), PyTorch 2.11.0+cu128,
  CUDA 12.8 driver. SSH via node IP `10.130.123.35:32516` (LoadBalancer IP is
  firewalled from the workstation).
- **Qwen endpoint discovered and restored.** Existing Run:ai workload
  `qwen38-27b12` (`Qwen/Qwen3.8-27B-FP8`) reachable only through the runai CLI
  port-forward + Caddy tunnel previously built for `hotc2026-lab`. Tunnel supervisor
  restarted; `http://127.0.0.1:18000/v1` healthy; chat completion + tool-call smoke
  tests pass. Run:ai CLI token valid until 2026-09-10 (refresh token present; if
  refresh fails, human must re-run `runai login remote-browser` — documented blocker
  contingency).
- **Repository created** at `/home/jovyan/work/causal-mind`; orchestration infrastructure
  adapted from the proven `hotc2026-lab` harness (task queue with atomic claims,
  per-worker worktrees, supervisor loops, Qwen client); direct Qwen tool-loop agent
  harness added for autonomous workers.
- **CM-0 epistemic seal** drafted: questions, definitions, hypotheses H1-H6, validation
  protocol frozen, claims registry initialized.

## 2026-09-10

- **NFS ownership conflict discovered.** Files created via `kubectl exec` (root) are
  not writable from the SSH session (jovyan) and vice versa; the NFS maps everything to
  uid 65534 (nobody). The original root `/home/jovyan/work/causal-mind` (`.git`,
  `reports/agents`, worktrees) became locked for jovyan. Decision: rebuild at a
  jovyan-owned root `/home/jovyan/work/causal-mind-v2`; the old root is a frozen
  snapshot. All git commands now use `safe.directory=*` (dubious-ownership guard).
- **Rebuild completed.** Tree, dot-dirs (`.home`, `.runai-cli`, `.caddy`), agent
  reports, queue state, and worktree deliverables copied; fresh venv via uv
  (jovyan-owned cache `/home/jovyan/work/.uv-cache-jovyan`); 53/53 tests pass, ruff
  clean; git re-initialized; 5 worktrees recreated under
  `/home/jovyan/work/worktrees/causal-mind-v2/`.
- **Harness fixes.** (1) Agent loop now nudges the model on an empty final message
  instead of stopping (causal smoke had terminated with no output). (2) `cm status` /
  `cm qwen` CLI dispatch bug (missing `args` parameter). (3) Planner git calls and all
  scripts set `safe.directory=*`.
- **Qwen token expired (2026-09-10 11:03Z); refresh token did not renew.** The
  main-netns tunnel died. Discovered the SSH session runs in a sidecar network
  namespace (main container's 127.0.0.1:18000 not visible), but the cluster gateway
  `cisco-ai-pod.cc-demos.com` (10.130.240.221) is directly reachable from it, so the
  tunnel was rebuilt WITHOUT Caddy: plain `runai workspace port-forward` bound to
  127.0.0.1:18000 inside the SSH netns. New self-healing supervisor
  (`scripts/qwen_tunnel_supervisor.sh`, direct mode) running.
- **Re-authentication.** Human completed `runai login remote-browser` via
  `scripts/runai_login_pty.py` (pty wrapper that stages the flow, captures the URL,
  and delivers the pasted code from `/tmp/runai-code.txt`). New token written
  2026-09-10 20:59Z.
- **Phase C complete.** All six agents smoke-tested end-to-end: researcher (GO, 7
  cycles), data (GO, 5), forecasting (GO, 9), causal (GO, 23 — re-run after the
  empty-message fix), reviewer (GO, 6), orchestrator (GO, 10). All six SMOKE tasks
  reviewed and drained to done.
