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
