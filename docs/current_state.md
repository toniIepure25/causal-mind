# Current State

## Project state

`CM5A_REAL_DATA_SMOKE_PASS`
(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`. OpenNeuro access is
RESTORED via authenticated selective acquisition; CM-5 proceeds to the
MRI-eligible cohort definition, metadata-first and outcome-independent.)

## 2026-09-14 handoff recovery (git)

- Previous session was lost to a context limit; unpushed pod commits `ea69195`
  (CM-5A selective OpenNeuro acquisition + real-data minimal smoke) and `5e88f72`
  (gitignore-data-neural) were preserved in `/home/jovyan/work/cm5a_push.bundle`
  (base `9c59300`, verified).
- Integrated through the authorized orchestrator bundle workflow (workstation
  clone of GitHub main `76066ac` -> merge of pod main `5e88f72` -> push).
  **GitHub main is now `a61753c`.** Pod main fast-forwarded to `a61753c`.
- Handoff integrity verified on pod: 112/112 tests pass (requires
  `HF_HOME=/home/jovyan/work/.hf-home`), ruff clean.
- The pod was recreated between sessions (now
  `orchestraiq-jupyter-ccd58f4b9-jbqtj`); the PVC `/home/jovyan/work` is intact.
  Node v20.11.1 restored at `/home/jovyan/work/.local/node`; `@openneuro/cli`
  4.30.2 + deps reinstalled at `causal-mind-v2/.tools/openneuro` (gitignored);
  the fetcher runs with
  `NODE_PATH=/home/jovyan/work/causal-mind-v2/.tools/openneuro/node_modules`.
- sub-001/sub-005 neural files re-verified after the pod recreation: all six
  large files (2 BOLD, 2 confounds TSV, 2 masks) HASH_MATCH their annex keys.
- OpenNeuro authenticated access verified healthy (snapshot tree API + URL
  resolution, no credential exposure).

## Current stage

Phase 2: CM-1 (data), CM-2 (non-neural next-thought prediction), and CM-3
(multi-step cognitive futures / Thought Predictive Horizon) complete and pushed.
CM-5 (neural) in progress: data-independent pipeline complete, real-data N=2
smoke complete, MRI-eligible cohort definition starting (metadata-first audit
of all 118 subjects).

## Validated results

- L0: Qwen endpoint `Qwen/Qwen3.8-27B-FP8` reachable at `http://127.0.0.1:18000/v1`
  (chat + tool calls); tunnel supervisor self-heals (direct port-forward, no Caddy).
- L0: task queue claim locking, worktree isolation, agent harness; all six agents
  smoke-tested (SMOKE-*-001).
- **CM-1 (L0 data integrity):** ds006067 audited across its two authoritative
  sources — OpenNeuro `ds006067 v2.0.0` (MRI) + OSF `a56rm` (behavioral). 118
  subjects; sentence-level transcripts (118), word-level (102), GPT ratings (118),
  human-validated ratings (18). Cohort integrity: 10/10 checks pass. Red-team GO.
- **CM-2 (L3):** past thought history (a k≈3 window of frozen MiniLM text
  embeddings) predicts next-thought semantics **above all baselines B0-B7**
  (0.3623 [0.3523, 0.3720] vs strongest 0.3265 [0.3149, 0.3381], non-overlapping
  CIs), out-of-sample, subject-disjoint (83/18/17, sealed), prospective;
  permutation null p=0.0000; reproduced from a clean process. Effect is modest;
  category arm unvalidated; no causal claim. Red-team GO.
- **CM-3 (L5):** cognitive history predicts **future** thought semantics T[t+h]
  above the strongest frozen baseline at **every** event horizon h=1..10, with a
  smooth monotonic decay of PredictiveGain (+0.0349 at h=1 → +0.0044 at h=10, all
  95% CIs excluding 0). **TPH_semantic ≥ 10 thoughts (~2 min)** — a lower bound,
  since the gain is still significant at the max tested horizon. Subject-disjoint
  (83/18/17 sealed), reproduced exactly; survives time-shuffled,
  transition-destroyed, and a stronger random-target null (p=0.0000). History
  depth saturates at k≈3; the predictive window is ~2 min in wall-clock time.
  Effect modest; small test set (n=17); no causal claim. Red-team GO.

## Failed hypotheses

(none yet — CM-2 and CM-3 are modest positives, not nulls)

## Active tasks

- CM-5 MRI-eligible cohort: metadata-first audit of all 118 subjects
  (availability + cheap confound/QC metadata only, NO neural outcomes),
  then freeze/seal eligibility, project the frozen CM-3 split, seal the cohort,
  and acquire eligible BOLD only.
- CM-5 decisive analysis (M0-M4, M4-M2 + residual test, NC1-NC6), red-team,
  claims decision.
- Optional CM-3 extensions (only if warranted): nonlinear/deep multi-horizon
  heads (justified only if they beat the linear model on held-out data); finer
  TPH resolution beyond h=10.

## CM-5 (neural) — in progress, real-data smoke complete

- **Status:** `CM5A_REAL_DATA_SMOKE_PASS`. OpenNeuro access restored via an
  authenticated selective acquisition route (API token configured on the pod,
  chmod 600, never printed/committed). Custom selective fetcher
  `scripts/cm5_fetch.js` enforces the hard invariant
  **requested dataset path == resolved S3 URL path** (mismatch => SKIP); the
  OpenNeuro API path-mismatch anomaly (e.g. requested `sub-001 ... bold.json`
  resolved to a `sub-127` object) is documented and regression-tested. Affected
  in-Git JSON files were sourced from the authoritative Git metadata clone
  (`/home/jovyan/work/ds006067_git`).
- **Real data on disk (gitignored `data/neural/`):** sub-001 + sub-005 MNI BOLD
  (~771 MB / ~791 MB), confounds TSV, brain masks, BOLD + confounds JSONs —
  all HASH_MATCH against annex keys (re-verified 2026-09-14).
- **N=2 real-data smoke:** the full pipeline (OpenNeuro BOLD -> confounds ->
  HRF-safe windows -> neural features -> M0-M4) ran end-to-end on
  sub-001/sub-005 (211 event rows; M2=0.8847, M4=0.8482, gain=-0.0365).
  **ENGINEERING SMOKE ONLY** — zero scientific interpretation; excluded from
  model selection, QC-threshold tuning, and all confirmatory decisions.
- **Frozen/sealed protocol** (`docs/protocol/cm5_frozen_protocol.md`, seal in
  `data/manifests/cm5_protocol_seal.json`): HRF-safe buffer B=6 s, neural
  window W=15 s, TR~1.5 s; primary alignment C (lagged neural history with HRF
  buffer); horizons h=1,3,5,10; models M0-M4; decisive contrast M4 vs M2 +
  mandatory residual test; negative controls NC1-NC6; subject-disjoint;
  subject-level inference (bootstrap/permutation); gates N0-N6.
- **Next (authorized):** define the MRI-eligible cohort WITHOUT inspecting
  neural prediction outcomes (criteria: data availability, file validity,
  temporal compatibility under B=6s/W=15s, imaging/motion QC, behavioral
  compatibility); download only cheap confound/QC metadata first; freeze +
  hash-seal eligibility criteria BEFORE decisive outcomes; project the frozen
  CM-2/CM-3 split (83/18/17) onto eligible subjects; produce the CM5 MRI COHORT
  SEAL; verify storage; then acquire sealed-eligible BOLD only.

## Blockers

- **Token lifecycle:** Run:ai CLI tokens expire ~daily; refresh tokens do NOT
  auto-renew in the CLI. When the token expires, a human must complete
  `runai login remote-browser` (open URL, paste code). Runbook:
  `docs/runbooks/qwen_tunnel.md`. The pod-side helper
  `scripts/runai_login_pty.py` stages the flow and waits for the code in
  `/tmp/runai-code.txt`.

## Key commit hashes

- `a61753c` GitHub main after CM-5A integration (2026-09-14 handoff recovery)
- `5e88f72` pod main before integration (gitignore-data-neural)
- `ea69195` CM-5A selective OpenNeuro acquisition + real-data minimal smoke
- `9c59300` CM-5A neural data recovery audit (bundle base)
- `23d20f1` CM-3 completion anchor (CM-5 protocol anchor)

## Exact reproducibility commands

```bash
# on the pod, via SSH as jovyan (sidecar netns)
cd /home/jovyan/work/causal-mind-v2
export PATH=/home/jovyan/work/.local/node/bin:$PATH
export NODE_PATH=/home/jovyan/work/causal-mind-v2/.tools/openneuro/node_modules
export HF_HOME=/home/jovyan/work/.hf-home
scripts/qwen_tunnel_supervisor.sh status
.venv/bin/python -m causal_mind.cli status
.venv/bin/python -m pytest
.venv/bin/python -m ruff check src tests scripts
node scripts/cm5_fetch.js --dry --subject=sub-001 --no-optional
```

## Environment notes

- Working root: `/home/jovyan/work/causal-mind-v2` (jovyan-owned). The original
  `/home/jovyan/work/causal-mind` is a frozen root-owned snapshot (NFS ownership
  split).
- Worktrees: `/home/jovyan/work/worktrees/causal-mind-v2/<worker>`.
- All git commands need `safe.directory=*` (NFS maps ownership to uid 65534);
  scripts and the planner set this automatically.
- The SSH session runs in a sidecar network namespace: the main container's
  127.0.0.1:18000 is NOT visible there. The tunnel supervisor binds the
  port-forward inside the SSH netns; the cluster gateway is reachable directly
  via `cisco-ai-pod.cc-demos.com` (no Caddy needed).
- Pod recreated 2026-09-13/14 (`orchestraiq-jupyter-ccd58f4b9-jbqtj`);
  ephemeral rootfs contents (system node, npm globals) were lost and restored
  onto the PVC (`/home/jovyan/work/.local/node`,
  `causal-mind-v2/.tools/openneuro`). The HF cache used by the MiniLM test is
  `/home/jovyan/work/.hf-home` (set `HF_HOME` accordingly).
