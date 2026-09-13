# Current State

## Project state

`CM3_PASS`
(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`. OpenNeuro S3 outage is
no longer a CM-2/CM-3 blocker — behavioral data is sourced from OSF `a56rm`.
OpenNeuro is still required for CM-5 neural analyses; the S3 retry is kept alive.)

## Current stage

Phase 2: CM-1 (data), CM-2 (non-neural next-thought prediction), and CM-3
(multi-step cognitive futures / Thought Predictive Horizon) complete and pushed.
Next: CM-5 (neural), which needs OpenNeuro `ds006067` MRI.

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
  (83/18/17 sealed), reproduced exactly; survives time-shuffled, transition-destroyed,
  and a stronger random-target null (p=0.0000). History depth saturates at k≈3;
  the predictive window is ~2 min in wall-clock time. Effect modest; small test set
  (n=17); no causal claim. Red-team GO.

## Failed hypotheses

(none yet — CM-2 and CM-3 are modest positives, not nulls)

## Active tasks

- CM-5 (neural): requires OpenNeuro `ds006067` MRI (S3 still down; retry kept alive).
  Goal: link the thought-state / prospective signal to concurrent fMRI.
- Optional CM-3 extensions (only if warranted): nonlinear/deep multi-horizon heads
  (justified only if they beat the linear model on held-out data); finer TPH
  resolution beyond h=10.

## CM-5 (neural) — in progress, data-independent pipeline complete

- **Status:** `CM5_DATA_INDEPENDENT_READY`. The fMRIPrep MNI BOLD content for
  ds006067 is currently inaccessible from the pod (OpenNeuro dataset API has no
  A record; public S3 content bucket returns 403 for the annex keys). A retry
  poller (`/home/jovyan/work/cm5_access_retry.sh`) is kept alive.
- **Access audit** (`docs/cm5_access_audit.md`): all 118 raw `events.tsv`
  (onset/duration/transcript in MRI seconds) + `participants.tsv` are real files
  in the GitHub mirror clone; fMRIPrep 23.2.1 derivative structure + annex keys
  known; BOLD content blocked pending API/S3 access.
- **Frozen/sealed protocol** (`docs/protocol/cm5_frozen_protocol.md`, seal in
  `data/manifests/cm5_protocol_seal.json`): HRF-safe buffer B=6 s, neural window
  W=15 s, TR~1.5 s; primary alignment C (lagged neural history with HRF buffer);
  horizons h=1,3,5,10; models M0-M4; decisive contrast M4 vs M2 + residual test;
  negative controls NC1-NC6; subject-disjoint; 1000 bootstrap / 1000 permutation /
  BH-FDR; gates N0-N6.
- **Implemented + unit-tested (synthetic, all pass, ruff clean):**
  - HRF-safe prospective neural-window builder (`src/causal_mind/neural/prospective_window.py`).
  - Fusion models M0-M4 + residual correction (`src/causal_mind/neural/fusion.py`).
  - Destructive negative controls NC1-NC6 (`src/causal_mind/neural/negative_controls.py`).
  - Neural feature ladder N1-N3: network / atlas / train-fitted PCA
    (`src/causal_mind/neural/features.py`).
  - End-to-end evaluation runner with a synthetic PASS
    (`data/scripts/run_cm5_evaluation.py --synthetic`): subject-disjoint
    IncrementalNeuralGain positive (0.4968) and collapses under every control.
  - BOLD validation (`data/scripts/cm5_validate_bold.py`) + acquisition
    (`data/scripts/cm5_acquire.sh`) for when access is restored.
- **Blocked:** fMRIPrep BOLD acquisition + real-data CM-5 run + red-team +
  claims decision (all pending OpenNeuro access restoration).
