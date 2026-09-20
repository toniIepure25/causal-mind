# Break-the-Chain: A Frozen Confirmatory Protocol for the Causal Redirection of a Predicted Thought

**Protocol (Paper 3).** Status: frozen, part of the `cm8-prehuman-v1.0` freeze. This is the
standalone protocol for the CM-8 confirmatory experiment. It is **designed and frozen but
not yet run** (blocked on ethics approval + pilot). No human data has been collected.

---

## 1. Objective

Test whether a **prediction-conditioned intervention** causally redirects a **predicted**
semantic thought trajectory. Primary question: does the observed future leave the frozen
predictor's predicted-future basin at a different rate under intervention than under
control?

## 2. Hypotheses and estimands

- **H1 (GENERAL-REDIRECT):** an endogenous, general redirection cue changes the BRP vs
  pooled CONTROL/SHAM. Estimand: **ATE_GENERAL**.
- **H2 (SPECIFIC-CUE):** an exogenous, specific cue changes the BRP vs pooled CONTROL/SHAM.
  Estimand: **ATE_CUE**. (Disclosed as potentially confounded by lexical priming; secondary.)
- **SHAM-alone sensitivity:** SHAM vs CONTROL (expected ≈ 0; a believable no-op).

## 3. Design

- **Type:** within-subject, randomized, 4 conditions: **CONTROL / SHAM / GENERAL-REDIRECT /
  SPECIFIC-CUE**.
- **Sample:** **N=20** participants, **24 trials** each.
- **Randomization:** fixed counterbalanced permutation, **seed 20260917**, deterministic
  (predictable by design; mitigation = blinding). Audited (perfect balance, max run 1).
- **Primary outcome:** **BRP** = P(observed future leaves the frozen predicted-future basin |
  condition).
- **Basin:** ball around the frozen forecast, radius = held-out 90th-percentile
  prediction-error norm (prospective; calibrated on VAL, h*=2, r_α=0.9911). Not tuned to
  outcomes.

## 4. Inference

- **Test:** subject-clustered permutation test, **B=10,000**, **two-sided α=0.05** (separate
  from the basin tail 0.10).
- **CIs:** subject-level bootstrap.
- **Type-I audit:** empirical type-I at α=0.05 = **0.047** (MC 95% CI [0.013, 0.080]),
  independently reproduced (alt-seed 0.040) → CALIBRATION PASS.
- **Power:** N=20 is under-powered for small effects (documented on the power surface;
  power rises more with N than trials; high ICC reduces power). **Not changed.**

## 5. Procedure (per trial)

1. Participant enters a thought (keyboard capture).
2. The **frozen** forecaster predicts the future thought state (h*=2) and defines the
   predicted-future basin.
3. The **frozen** randomization assigns the condition.
4. The intervention (none / sham / general redirect / specific cue) is delivered.
5. The observed future thought is captured; BRP is computed (inside/outside the basin).
6. The trial is finalized **atomically** (append-only JSONL; no duplicate finalization).

The engine is **offline** (no Qwen/LLM/internet in the loop); total critical path
**p95 = 478 ms**, cold first trial **876 ms**.

## 6. Pre-human validation (10/10 gates)

- **Ghost pilot:** BRP_control held-out TEST = 0.0785 (target 0.10), 118 ghost participants,
  5,964 forecasts, 0 missing events.
- **Monte Carlo:** type-I under the null calibrated (finite-B artifact ruled out).
- **Realtime engine:** offline + transactional + full trial lifecycle.
- **Chaos:** 7/7 injected faults handled loudly (no partial trial becomes analysis-valid).
- **Privacy:** 12/12 (PII detection/redaction, pseudonymization, encryption at rest, no
  remote telemetry).
- **Clean-room:** bit-identical re-fit (SHA-verified).
- **BRP red team:** 7/9 adversarial cases produce a misleading high BRP; secondary
  diagnostics (cosine-direction, Mahalanobis, persistence, novelty) reveal the modes. BRP
  stays PRIMARY; the diagnostics are reported alongside.

## 7. Analysis plan (pre-registered)

- Primary: ATE_GENERAL and ATE_CUE vs pooled CONTROL/SHAM, subject-clustered permutation,
  B=10,000, two-sided α=0.05.
- Secondary: SHAM vs CONTROL (no-op check); BRP secondary diagnostics; manipulation check;
  report-reactivity check.
- **Blinding:** analysis blinding + experimenter blinding (the fixed permutation is
  predictable by design; blinding is the mitigation).
- **Pilot (CM-8P):** a small, gated run (3–5 participants) whose only purpose is operational
  GO/ITERATE/STOP — **not** an analysis of the ATE.

## 8. Ethics and privacy

- University-of-Vienna ethics package in `docs/ethics/` (frozen protocol v1.0, participant
  information + consent, GDPR data-protection plan, risk assessment, debrief, prereg,
  software-freeze manifest, dry run ALL PASS).
- **Privacy-by-design:** no raw thought text leaves the machine; embeddings only;
  pseudonymized (salted hash, encrypted salt); encryption at rest; access audit; complete
  deletion; no remote LLM/telemetry.
- **Submission authority:** for a Master's thesis, the supervisor / responsible study-law
  body submits (the researcher prepares, does not submit).

## 9. What this protocol will and will not show

- **Will show:** whether a prediction-conditioned intervention changes the BRP vs control,
  with a pre-registered, calibrated, randomized design.
- **Will not show:** a free-will result; a claim that the intervention "proves" anything
  about consciousness; a causal claim from the (non-identifiable) observational data.
- **A null is a result.** The protocol is not to be changed to chase a positive.

## 10. Status and gate

- **Status:** `CM8R_PREHUMAN_HARDENED` (10/10 gates). **Not yet run.**
- **Gate to run:** supervisor sign-off → ethics approval → pilot authorization (CM-8P) →
  confirmatory run (CM-8H).
