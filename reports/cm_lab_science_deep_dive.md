# CM-LAB Scientific Deep Dive — Final Scorecard (CM-LAB §84-88)

**Overall: `CMLAB_SCIENTIFIC_DEEP_DIVE_COMPLETE`** (2026-09-24)

The scientific deep dive (sections 25-88) rigorously attacked the remaining assumptions of the
CM-2/CM-3 predictive-dynamics finding. All work is on the frozen ds006067 split (83/18/17, CM-2
seal), TRAIN-only fitting, no human data, no result shopping. New claims C-102..C-107; C-101
revised. The frozen `cm8-prehuman-v1.0` release and the CM-8 confirmatory protocol are untouched
(`CM8_CONFIRMATORY_INTACT`).

## Workstream decisions

| § | Workstream | Decision | Claim | Report |
|---|---|---|---|---|
| 25-28 | XVAL-1 inference adjudication | `CMXVAL_PARTIAL_REPLICATION` | C-101 (revised) | `reports/cm_xval/cm_xval_inference.json` |
| 32-35 | Uncertainty / calibration / selective | `CMUNC_WEAK` | C-102 | `reports/cm_uncertainty/cm_uncertainty.json` |
| 29-31 | Representation + metric robustness | `CMREP_PARTIAL` | C-104 | `reports/cm_representation/cm_representation.json` |
| 36-40 | Personalization + reliability | `CMPERS_NULL` | C-103 | `reports/cm_personalization/cm_personalization.json` |
| 41,43-47 | Local dynamics | `CMDYN_LINEAR_PREDICTION_DOMINANT` | C-105 | `reports/cm_dynamics/cm_dynamics.json` |
| 48-49 | Error taxonomy + error prediction | `CMERR_WEAKLY_PREDICTABLE` | C-106 | `reports/cm_error_taxonomy/cm_error_taxonomy.json` |
| 63-71 | Oracle selective + recursion + theory | `CMORACLE_SELECTIVE_ONLY` | C-107 | `reports/cm_oracle/cm_oracle.json` |
| 50-59 | Standards + leakage scanner | `CMLEAK_PASS` / `CMSTD_IN_PLACE` | — | `reports/cm_leakage_scan/cm_leakage_scan.json` |
| 60 | Disaster recovery (2nd independent run) | `CMLAB_DISASTER_RECOVERY_REPRODUCED` | — | `reports/disaster_recovery_second_run.md` |
| 83 | CM-8 confirmatory no-drift | `CM8_CONFIRMATORY_INTACT` | — | `reports/cm8_no_drift/cm8_no_drift.json` |

## Net scientific picture

The CM-2/CM-3 predictive-dynamics finding (a linear model over frozen MiniLM embeddings beats
the strongest frozen baseline at every horizon) is **REAL but bounded**:

1. **Subject-identity-driven, not temporal.** The external-validation gain survives subject-level
   inference, but the null family shows it is driven by **subject identity** (N0/N5 rejected),
   while within-subject temporal/transition nulls are NOT rejected (N1-N4, N6). The model
   exploits "who this subject is," not "how this subject's thoughts transition."
2. **Representation-specific (semantic).** The gain is large for semantic embeddings (MiniLM,
   mpnet) and small for lexical/topic (TF-IDF, NMF) — a 5.9x effect-size ratio. The finding is
   tied to the semantic representation, not a generic property of the text.
3. **Not personalizable.** Per-subject personalization actively HURTS (all gains negative) —
   session drift dominates the small adaptation data.
4. **Weakly confidence-gateable.** The model cannot reliably know in advance which forecasts will
   be poor (best AUROC 0.585; bootstrap disagreement is anti-calibrated). The dominant large-error
   mode is **novelty** (rare state, abrupt jump).
5. **Oracle-usable only selectively and non-recursively.** A modest selective oracle (top-10%
   confidence → +0.039) exists, but recursive rollout is unstable (L0→L3 degradation 0.092). For
   the human Oracle work (CM-8P), the model must be used in a **selective, non-recursive** mode.

These are **negative and bounding results**, reported as results (not bent). They define what the
model can and cannot do before any human work.

## Platform integrity (unchanged)

- `CM8_CONFIRMATORY_INTACT`: forecaster config, freeze confirmatory config, code SHAs,
  randomization manifest, registry SHAs all intact; no real human-data collection.
- `CMLAB_DISASTER_RECOVERY_REPRODUCED`: fresh clone → bootstrap → validate → integrity, all green.
- `CMLEAK_PASS`: data-leakage scanner (L1-L5) passes across all 7 deep-dive scripts.
- 12 frozen artifacts SHA-verified unchanged; lint ratchet 32/32; full validation PASS.

## What this does NOT do

- Does NOT change C-001..C-012, the frozen CM-8 confirmatory protocol, or the
  `cm8-prehuman-v1.0` release.
- Does NOT collect any human data.
- Does NOT claim free will (no free-will claim).
- Does NOT extend the English MiniLM result to other languages/datasets without a dedicated
  replication (next-dataset policy, §73).

## Remaining work (human-gated)

The ONLY remaining scientific work is the **human experiment** (CM-8P pilot + CM-8 confirmatory),
gated on: (1) supervisor sign-off, (2) ethics approval (submission deadline 5 Oct 2026), and
(3) pilot authorization. The deep dive has made the pre-human record as rigorous as possible
without human data.

**Verification:** `bash scripts/validate_project.sh`; `.venv/bin/python data/scripts/cm_deep_dive_runner.py`
(full) or `--demo` (fast).
