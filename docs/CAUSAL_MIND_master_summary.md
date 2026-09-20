# CAUSAL MIND — Master Research Summary

**Pre-human research freeze.** This document is the single authoritative summary of the
CAUSAL MIND program as of the `cm8-prehuman-v1.0` release (git `8a9d5dd`, 2026-09-20).
It contains **no human data** and **no CM-8 protocol changes**. All numbers below are
copied verbatim from the committed reports under `reports/`.

---

## 1. What this program is

CAUSAL MIND is a research program that asks two linked questions about the human thought
stream:

1. **Prediction.** Can the future of a person's thought stream be predicted from its
   recent past — the next thought, and thought states several thoughts ahead?
2. **Intervention.** Can a prediction-conditioned intervention change the future thought
   state, and can that effect be estimated causally?

The program is built entirely on **public cognitive-science datasets** (the OSF `a56rm`
thought-diary corpus and the OpenNeuro `ds005494` semantic-priming corpus) and on
**synthetic worlds** for method validation. **No human data has been collected.** The
program stops at a formally frozen, ethics-ready, pre-human state.

## 2. The program (phases and states)

| Phase | Question | State | One-line result |
| --- | --- | --- | --- |
| CM-1 | Is the data usable? | `CM1_PASS` | Integrity/alignment checks pass. |
| CM-2 | Can we predict the next thought? | `CM2_PASS` | Held-out semantic cosine 0.362 [0.352, 0.372], beats all 8 baselines. |
| CM-3 | Can we predict several thoughts ahead? | `CM3_PASS` | Model beats the strongest baseline at every horizon (h=1..10). |
| CM-5 | Do neural features add value? | `CM5_NULL` | No incremental value (mean gain −0.088, all subjects negative). |
| CM-6 | Which edges are causally identifiable? | `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION` | 0/84 candidate edges identifiable (unmeasured confounding). |
| CM-7 | Does a public intervention work? | `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT` | ATE −0.039 [−0.079, 0.002], p=0.073; method validated. |
| CM-8 | Pre-Oracle / Break-the-Chain | `CM8_ETHICS_PACKAGE_READY` | Supervisor-ready University-of-Vienna ethics package; frozen protocol v1.0. |
| CM-8R | Pre-human hardening | `CM8R_PREHUMAN_HARDENED` | 10/10 pre-human gates pass; forecaster frozen + reproducible. |
| CM-9A | Synthetic Oracle lab | `CM9A_SYNTHETIC_ORACLE_READY` | 4 oracle conditions × 11 agent policies, RPR/PIE measured. |

## 3. Key results (positive)

- **CM-2 next-thought prediction.** A linear transition model (k=3, α=100) on the
  MiniLM-L6-v2 thought-state embedding reaches held-out **semantic cosine accuracy
  0.362 [95% CI 0.352, 0.372]** on 118 subjects / 6,436 thoughts (subject-disjoint
  83/18/17 split, seal `67505261…`). It beats the strongest baseline (B0 marginal,
  0.317 [0.308, 0.325]) by ≈0.046 and all 8 baselines.
- **CM-3 multi-horizon forecasting.** The same model beats the strongest horizon-specific
  baseline at every horizon. Gains over the strongest baseline: h=1 +0.035 [0.025, 0.045],
  h=2 +0.026 [0.021, 0.032], h=3 +0.015 [0.009, 0.022], h=4 +0.011 [0.007, 0.016],
  h=5 +0.009 [0.004, 0.014]. Gains decay smoothly with horizon (the expected signature of
  a real, finite-horizon signal).
- **CM-8R pre-human hardening (10/10 gates).**
  - *Ghost pilot:* BRP_control held-out TEST = **0.078** (target basin tail 0.10) over
    118 ghost participants, 5,964 forecasts, 0 missing events — the calibrated
    "break-the-chain" rate under no intervention is close to the target.
  - *Monte Carlo:* type-I error calibrated at α=0.05 (finite-B artifact ruled out).
  - *Realtime engine:* offline, transactional, full trial lifecycle; **total critical
    path p95 = 478 ms, cold first trial = 876 ms** (local MiniLM + ridge forecaster; no
    LLM/API/internet in the loop).
  - *Chaos:* **7/7** injected faults handled loudly (no partial trial becomes
    analysis-valid).
  - *Privacy:* **12/12** tests pass (PII detection/redaction, pseudonymization,
    encryption at rest, no remote telemetry).
  - *Clean-room:* a from-scratch re-fit of the forecaster is **bit-identical** to the
    frozen artifact (SHA-verified).
- **CM-9A synthetic Oracle lab.** A synthetic world with 4 oracle conditions
  (HIDDEN/REVEAL/VETO/REDIRECT) and 11 agent policies (O0–O10) measures the Relative
  Prediction Ratio (RPR) and Prediction–Intervention Effect (PIE) per policy. The lab is
  ready to certify which synthetic interventions are detectable before any human trial.

## 4. Key results (negative — accepted, not reopened)

- **CM-5 neural incremental value: NULL.** Adding fMRI-derived neural features to the
  thought-state model provides **no incremental predictive value**: primary neural set N2
  at h=1 has mean gain **−0.088 [−0.106, −0.072]**, permutation p = 1.0, Cohen's d =
  −2.51, **0/16** test subjects positive. The negative gain is replicated by all negative
  controls (subject permutation, temporal shift, block permutation, neural randomization),
  so it is a genuine null, not an artifact.
- **CM-6 causal identification: NO IDENTIFICATION.** Of **84** candidate lagged edges in
  the observational thought stream, **0** are causally identifiable: every backdoor-blocking
  set requires at least one unobserved latent node (unmeasured confounding, no
  randomization). The observational structure is reported as **candidate, not causal**.
- **CM-7 public intervention: NULL (method validated).** On the public `ds005494`
  semantic-priming corpus (20 subjects, 26 sessions, 3,330 pairs, integrity match rate
  0.9994), the primary ATE is **−0.039 [95% CI −0.079, 0.002]**, two-phase permutation
  p = **0.073** (not significant). The **method** (integrity audit, two-phase permutation,
  list- and subject-level bootstrap) is validated; the **effect** is null.

## 5. What is frozen (immutable)

- **CM-8 confirmatory protocol v1.0** (Workstream A): primary endpoint = BRP at h*=2;
  4 conditions (CONTROL/SHAM/GENERAL/CUE); basin tail 0.10; α = 0.05 two-sided;
  B = 10,000 permutations; N = 20, 24 trials; seed 20260917; fixed counterbalanced
  randomization; estimands ATE_GENERAL and ATE_CUE vs pooled CONTROL/SHAM.
- **Participant-facing forecaster:** LinearMultiHorizon, k=3, α=100, horizons 1–10;
  basin radius calibrated on the held-out VAL split.
- **Frozen artifacts** (SHA-256 in `docs/releases/cm8_prehuman_v1.md`): forecaster
  config + weights, forecasting freeze manifest, randomization manifest, CM-2 split seal,
  and the seven frozen source files.

## 6. What is blocked (the only remaining blockers to human data)

1. Supervisor / institutional sign-off.
2. Ethics approval (University of Vienna Ethics Committee).
3. Pilot authorization (CM-8P, gated).

No human data has been collected. The CM-8 confirmatory protocol is unchanged.

## 7. How to reproduce

See `docs/releases/cm8_prehuman_v1.md` for the exact commands (clean-room re-fit,
readiness scorecard, realtime engine, Oracle lab, full test suite + ruff). All
reproducibility is from frozen local artifacts; no network access is required at
inference time.

## 8. Where to start

- Supervisor: `docs/supervisor/START_HERE.md`
- Release freeze: `docs/releases/cm8_prehuman_v1.md`
- Claim-level evidence: `docs/claims/evidence_matrix.md`
- Paper drafts: `papers/paper1_predictive_dynamics/`, `papers/paper2_prediction_to_intervention/`,
  `papers/paper3_break_the_chain_protocol/`
- Negative results: `docs/science/negative_results.md`
- Limitations: `docs/science/limitations.md`

---

*This summary is a freeze document. It does not modify any frozen phase. Any change to the
frozen components after this tag requires a new tag and a documented amendment.*
