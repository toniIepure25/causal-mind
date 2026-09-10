# Validation Protocol (frozen, CM-0)

This protocol is frozen before any final test outcomes are inspected. Changing it after
inspection requires an ADR, a research-log entry, and a fresh holdout.

## 1. Splits

1. **Subject-disjoint by default.** Train/val/test participants are disjoint sets.
   Never use random row splits on temporal data.
2. **Within-subject temporal order is never crossed.** For any subject in a split, all
   of that subject's samples stay in that split.
3. **Repeated subject-level splits.** Where subject count permits, report results over
   >= 5 repeated subject-level randomized splits (fixed seeds, recorded).
4. **Untouched final holdout.** If dataset size permits, one subject-level holdout is
   reserved and evaluated exactly once per frozen protocol version.
5. **Session identity is a confound, not a feature.** Models must not be allowed to
   shortcut on session/run id; session is either removed or included as a controlled
   covariate, documented per experiment.

## 2. Leakage controls (audited by the reviewer before any result is reported)

- Temporal leakage: no future information in features (lag audit, BOLD hemodynamic lag
  grid for neural features).
- Subject leakage: zero shared participants across splits (automated check in
  `causal_mind.utils.splits`).
- Duplicate samples: exact and near-duplicate transcript detection.
- Transcript leakage: no target-side text in features (e.g., no next-thought words in
  current features).
- Preprocessing leakage: all preprocessing fit on train only; transforms applied
  identically to val/test.
- Label contamination: annotation provenance check; no cross-run label sharing.
- Autocorrelation artifacts: metrics reported with effective-sample-size correction or
  block-bootstrap where applicable.
- Speaker/motor confounds: documented; motor-artifact features flagged.

## 3. Statistics

- Primary inference: **permutation tests** on the subject-level effect (null: shuffle
  subject labels or temporal order, respecting the split structure).
- Uncertainty: **bootstrap CIs** (subject-level resampling, >= 1000 resamples, fixed
  seed).
- Effect sizes reported alongside p-values (e.g., AUC difference, log-odds, R2).
- Multiple comparisons: dimension/horizon grids use a pre-declared primary dimension
  and a secondary family with FDR control.
- Calibration: reliability diagrams + expected calibration error for probabilistic
  forecasts.

## 4. Controls

- **Negative control:** shuffled labels must yield chance-level skill.
- **Permutation control:** permuted temporal order must destroy skill.
- **Baseline floor:** every model is compared against the full baseline battery
  (B0-B5) in the same run.
- **Fresh-process replication:** headline results are re-run from a clean process with
  the recorded manifest before being marked validated (GATE F).

## 5. Experiment manifests

Every experiment writes `experiments/manifests/<exp-id>.yaml` containing: git SHA,
config (full), dataset version + checksum, split definition + seed, model + seed,
environment (python, torch, key packages), metrics, wall time, and the reviewer's
audit status.

## 6. Gates

| Gate | Criterion |
| --- | --- |
| A — Data integrity | All subject IDs, temporal alignments, and splits validated by automated checks |
| B — Non-neural signal | History predicts future thought above trivial baselines (H1) |
| C — Robust generalization | Effect survives subject-disjoint testing + repeated splits |
| D — Multi-step futures | >= 1 dimension above baseline beyond the immediate next state (H2) |
| E — Neural incremental value | Brain features improve prospective prediction beyond history/context (H3) |
| F — Replication | Result reproduces under frozen protocol in an independent rerun |

Only after A-F does causal-intervention development (CM-8 onward) become the critical
path.
