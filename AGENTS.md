# AGENTS — CAUSAL MIND

## Global rules

- Project root (pod): `/home/jovyan/work/causal-mind`. Worktrees under
  `/home/jovyan/work/worktrees/causal-mind/<worker>`.
- Never print, commit, or log passwords, API keys, bearer tokens, SSH keys, Run:ai
  authentication, Kubernetes secrets, or any token-bearing file.
- Agents must not read `/home/jovyan/.runai`, `/home/jovyan/.runai-proxy`, SSH keys,
  Kubernetes config, or hidden credential files.
- Do not modify Kubernetes workloads, the Qwen server, NVIDIA drivers, or unrelated
  projects (`hotc2026-lab`, `pnpl2026-lab`, `FMRI2images*`, etc. are read-only references).
- Do not expose services publicly. Bind local tooling to `127.0.0.1`.
- All caches and scratch go under the project PVC (set `TMPDIR`, `PIP_CACHE_DIR`,
  `XDG_CACHE_HOME`, `HF_HOME`, `TORCH_HOME` inside `/home/jovyan/work`).
- Git on this NFS: prefix with `git -c safe.directory=*` when ownership maps to nobody.

## Roles

- `orchestrator`: maintains the task DAG, gates, claims registry, merges validated work.
- `researcher`: literature and dataset audits, novelty matrix, hypothesis formalization.
- `data`: dataset acquisition, manifests, checksums, loaders, temporal alignment.
- `forecasting`: thought-state representations, baselines, temporal models, calibration.
- `causal`: DAGs, identification assumptions, statistical gates, power analysis.
- `reviewer`: red team. Has authority to BLOCK any result. Audits leakage first.

## Scientific discipline

- Every claim gets a level (0-8) in `docs/claims_registry.md`. Never inflate.
- Subject-disjoint splits only. Never random row splits on temporal data.
- A negative result is a result. Do not bend gates to save a hypothesis.
- The reviewer's leakage audit must pass before any result is reported as validated.

## Allowed defaults

Read files, search, inspect git status/diff/log, run pytest/ruff, execute project-local
Python, write within the task's `allowed_paths`.

## Disallowed defaults

No git push from agents (orchestrator/human pushes), no force-push, no recursive deletes
outside the project, no credential access, no Kubernetes mutation, no modifying the Qwen
tunnel or unrelated projects.
