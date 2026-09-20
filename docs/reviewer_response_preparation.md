# Reviewer Response Preparation

A consolidated response bank for every anticipated reviewer concern, mapped to the evidence
that answers it. Use this to draft real reviewer responses. Part of the
`cm8-prehuman-v1.0` freeze.

## How to use

For each concern, the response cites the exact evidence (report / value / document). Keep
responses short, cite the value, and never raise the claim level to win an argument.

## Response bank

### R1. "The prediction effect is too small."
- **Response:** The contribution is the *establishment* of a real, finite, forecastable
  signal and its *horizon* (TPH_semantic ≥ ~10 thoughts / ~2 min), not its magnitude. The
  gain is reported against the *strongest* horizon-specific baseline with subject-level CIs
  excluding 0 at every horizon, and it decays **smoothly and monotonically** (h=1 +0.0349 →
  h=10 +0.0044) — the signature of a real finite-horizon signal. The effect is explicitly
  described as modest.
- **Evidence:** `reports/cm3_results.json`; `docs/CAUSAL_MIND_master_summary.md` §3.

### R2. "The test set is tiny (n=17)."
- **Response:** The split is sealed and subject-disjoint (no leakage); inference is
  subject-level (no pseudo-replication); the result survives three nulls (p=0.0000). n=17 is
  reported as a limitation. A larger-N replication is the next step (power surface guides N).
- **Evidence:** `data/manifests/cm2_split_seal.json`; `reports/cm8r_power_surface/`.

### R3. "You can't claim causation."
- **Response:** We make **no** causal claim from the observational data (0/84 edges
  identifiable). The causal evidence is (a) the *method* validated on a randomized public
  dataset (CM-7) and (b) the *frozen randomized* confirmatory design (CM-8, not yet run).
  The human causal result does not exist yet.
- **Evidence:** `reports/cm6_observational_results.json` (analysis_7); `reports/cm7_results.json`.

### R4. "The BRP is a strange estimand with failure modes."
- **Response:** The BRP is the pre-registered primary estimand because the intervention's
  target is the *predicted* trajectory. It is calibrated (ghost pilot BRP_control ≈ 0.0785 ≈
  0.10 target) and is **always** reported with secondary diagnostics (cosine-direction,
  Mahalanobis, persistence, novelty). The 7/9 adversarial failure modes are disclosed.
- **Evidence:** `reports/cm8r_ghost_pilot/`; `reports/cm8r_brp_redteam/`.

### R5. "The CM-7 validation is on a weird clinical dataset."
- **Response:** CM-7 validates the *method's structure* (randomized identification, leakage
  audit, destructive controls, subject-clustered inference), not the *thought* hypothesis.
  The specific effect is a null (stated). Caveats (clinical iEEG, no sham, retrieved not
  free state) are stated. What transfers to CM-8 is correctness under randomization.
- **Evidence:** `reports/cm7_results.json`; `docs/claims/evidence_matrix.md` (C-010).

### R6. "This is a free-will project in disguise."
- **Response:** We make **no** free-will claim (proven or disproven); it is out of scope and
  listed as UNKNOWN. The claim ceiling is L0–L6. The claim-language linter enforces this
  (0 BLOCK-level free-will overclaims).
- **Evidence:** `docs/science/known_unknowns.md`; `data/scripts/cm_pub_claim_linter.py`.

### R7. "The synthetic Oracle lab is not science about humans."
- **Response:** It is a *separate* research direction, explicitly synthetic (no real-human
  claim). It is useful for choosing detectable interventions and interpreting the BRP. It is
  clearly separated from the CM-8 confirmatory experiment.
- **Evidence:** `reports/cm9a_oracle_lab/`; `papers/oracle_theory/outline.md`.

### R8. "Is the forecaster tuned on the test split?"
- **Response:** No. The forecaster is a frozen artifact (SHA-verified); a clean-room re-fit
  is bit-identical; hyperparameters were selected on VAL only; TEST was never used for
  fitting/tuning.
- **Evidence:** `reports/cm8r_cleanroom/`; `artifacts/cm8_forecasting_freeze_manifest.json`.

### R9. "Are the splits really subject-disjoint and sealed?"
- **Response:** Yes. Subject-disjoint (no subject in more than one split) and sealed (seal
  `67505261…`, SHA-verified). No random row splits on temporal data.
- **Evidence:** `data/manifests/cm2_split_seal.json`.

### R10. "Can I reproduce the key numbers?"
- **Response:** Yes. Every key number maps to a committed script + frozen artifact
  (reproducibility traceability table). Commands in `docs/releases/cm8_prehuman_v1.md`.
  Full test suite + `ruff` pass. No network at inference.
- **Evidence:** `docs/claims/evidence_matrix.md`; `docs/releases/cm8_prehuman_v1.md`.

### R11. "What about the negative results — are you hiding them?"
- **Response:** No. The CM-5 neural null, the CM-6 non-identifiability, and the CM-7 null
  effect are all reported as results with exact values, in the master summary, the evidence
  matrix, and the papers. None are reopened.
- **Evidence:** `docs/science/negative_results.md`.

### R12. "N=20 is under-powered for the confirmatory run."
- **Response:** Yes, documented on the power surface (power rises more with N than trials;
  high ICC reduces power). N=20 is the frozen design; a null could be under-power, not a
  true null. We do not change N to chase power.
- **Evidence:** `reports/cm8r_power_surface/`; `docs/science/limitations.md`.

## General response rules

- Cite the exact value and the report; do not paraphrase numbers.
- Never raise the claim level to win an argument.
- A null is a result; do not defend a null as if it were a failure.
- If a concern is valid, concede it and state the limitation; do not argue it away.
