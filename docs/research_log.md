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

## 2026-09-14

- **Handoff recovery (git).** Previous session lost to a model context limit.
  Unpushed pod commits `ea69195` (CM-5A selective OpenNeuro acquisition +
  real-data minimal smoke) and `5e88f72` (gitignore-data-neural) were preserved
  in `/home/jovyan/work/cm5a_push.bundle` (base `9c59300`). Verified the bundle
  on the pod, cloned GitHub main (`76066ac`), merged pod main `5e88f72` into it
  (clean; no file overlap), and pushed. **GitHub main is now `a61753c`**; pod
  main fast-forwarded to the same SHA via a sync bundle (the pod repo has no
  GitHub remote by policy; pushes go through the workstation).
- **Handoff integrity check.** 112/112 tests pass on the pod (the MiniLM
  integration test needs `HF_HOME=/home/jovyan/work/.hf-home`); ruff clean.
- **Pod recreation discovered.** The pod was recreated between sessions
  (`orchestraiq-jupyter-ccd58f4b9-jbqtj`); the PVC is intact but the ephemeral
  rootfs lost the system node install. Restored node v20.11.1 at
  `/home/jovyan/work/.local/node` and reinstalled `@openneuro/cli@4.30.2` +
  `node-fetch@2` + `mkdirp` into the gitignored
  `causal-mind-v2/.tools/openneuro` (run with `NODE_PATH`).
- **Neural data re-verification.** All six large sub-001/sub-005 files
  (BOLD x2, confounds TSV x2, masks x2) re-hashed: all HASH_MATCH against the
  annex keys in `data/manifests/cm5_minimal_neural_files.tsv`.
- **OpenNeuro auth health.** Authenticated snapshot-tree API call succeeds
  (dry-run of `scripts/cm5_fetch.js`); the URL-path identity guard remains
  active (the known `bold.json` path-mismatch anomaly still reproduces and is
  skipped). No credentials exposed.
- **Next.** CM-5 MRI-eligible cohort: metadata-first audit of all 118 subjects
  (availability + cheap confound/QC metadata only), freeze + hash-seal
  outcome-independent eligibility criteria, project the frozen CM-3 split
  (83/18/17), seal the cohort, verify storage, then acquire eligible BOLD only.

## 2026-09-14 — CM-5 decisive analysis: clean NULL (no incremental neural value)

- **MRI-eligible cohort (outcome-independent).** Metadata-first audit of all
  118 subjects (availability + confounds QC + HRF-safe target counts). Frozen
  eligibility criteria (CM5-ELIG-1, hash-sealed): data availability (URL-path
  identity guard), file validity, >=20 steady-state HRF-safe targets (AM-1:
  onset>=36s), severe-motion screen (mean FD>1.0mm), behavioral compatibility.
  Excluded: sub-002 (OpenNeuro pointer-object anomaly, guard-fire), sub-067/
  087/110 (<20 targets), sub-089 (mean FD 1.207mm). Cohort 113 (79/18/16),
  sealed (reports/cm5_cohort_seal.json).
- **BOLD acquisition.** All 113 subjects' preproc BOLD + masks downloaded via
  the guarded, hash-verified, resumable fetcher (226 files, 0 mismatches, 0
  hash failures, 87.5 GB). Storage verified (87.5 GB vs ~102 TB free).
- **Post-acquisition gates (pre-registered, outcome-independent).** F2 tSNR
  gate excluded 6 (tSNR < 5th percentile; CM5-F2-TSNR-1). Cohort-level
  N-GATE-1 alignment audit found sub-036 with 2 OSF thoughts lacking a raw MRI
  event (CM5-ALIGN-1, excluded). Final cohort 106 (73/17/16).
- **Decisive result (CM5_NULL).** IncrementalNeuralGain (M4-M2) is NEGATIVE at
  every horizon h=1,3,5,10 for the primary N2 (Schaefer-400): -0.088/-0.085/
  -0.085/-0.090 (95% CIs exclude 0; 0/16 test subjects positive). Capacity
  ladder: N1 (7 nets) ~-0.001, N3 (PCA-50) ~-0.016, N2 (400) ~-0.085 — the
  degradation scales with dimensionality (noise signature, not a real signal).
  NC4 (nuisance-only) -> 0; NC1/2/3/5/6 preserve the negative gain (no
  correspondence to destroy). M0=0.32 (behavior), M2=0.32, M4=0.23.
- **Red-team: GO (conditional).** Fixed a CI-reporting bug (bootstrap_ci
  returns mean,lo,hi) and removed a post-cutoff speech feature (lag-to-next-
  onset). Confirmed no leakage (HRF-safe window, causal z-score, N3 fit on
  train only), the negative gain is expected Ridge noise (linear per-dim cost),
  and the null is strongest where power exists (N1/N3). Licensed claim is a
  scoped negative L5 result; NOT licensed: "brain has no prospective info"
  (underpowered for small high-dim effects), any causal/free-will claim.
- **Reproducibility.** 112/112 tests pass; synthetic end-to-end (injected
  neural signal) gives positive gain that collapses under all controls — the
  pipeline can detect a real signal.
- **Next.** Commit + push the CM-5 null. The neural incremental-value question
  is answered (null) for this task/window/horizons/baseline.
