# CM-8 Preregistration — FINAL (v1.0 — FROZEN for ethics submission)

- **Version:** 1.0. Sealed (hash) at ethics submission. No modification without amendment.
- **Companion protocol:** `docs/ethics/cm8_research_plan.md`.

## 1. Hypotheses

- **H1 (endogenous):** `ATE_GENERAL > 0`.
- **H2 (exogenous):** `ATE_CUE > 0`.
- **H3 (sham no-op):** SHAM ≈ CONTROL.
- **H4 (persistence):** redirection persists beyond one step, not explained by cue repetition.

## 2. Primary analysis

- **Estimands:** `ATE_GENERAL` and `ATE_CUE` (BRP difference vs pooled CONTROL/SHAM),
  estimated separately. Pre-specified sensitivity: the same ATEs vs the SHAM-alone
  reference. If H3 (SHAM vs CONTROL) is significant, the SHAM-alone reference is the
  primary.
- **Inference:** subject-clustered permutation test (permute condition labels within
  subjects; **B = 10,000** in the confirmatory analysis). **Two-sided, α = 0.05.**
- **Primary horizon:** `h*` frozen at seal (target 2). The continuous basin distance
  `D(t, h*)` is a secondary outcome with the same inference.
- **No post-treatment conditioning:** the primary ATE is NOT conditioned on effort,
  perceived success, or any post-intervention variable.

## 3. Statistical calibration audit (independently reproduced)

- **Primary test level: α = 0.05 (two-sided).** This is SEPARATE from the basin tail
  (a design parameter, 0.10, which sets BRP_control ≈ 0.10).
- **BRP calibration:** BRP_control = 0.0989 (target 0.10); `r_α` = the held-out 90th
  percentile of the predictor's error norm. Correct.
- **Type-I error at α = 0.05:** 0.047 (Monte-Carlo 95% CI [0.013, 0.080], SE 0.017,
  n_sims = 150, B_PERM = 200); independent alt-seed reproduction 0.040 (CI [0.009, 0.071]).
  **Compatible with 0.05.** An earlier cited 0.113 was the type-I error at the 0.10 level
  (the basin tail and test level had been conflated); it is NOT the α=0.05 type-I error.
- **Type-I error at α = 0.10:** 0.100 (CI [0.052, 0.148]) — compatible with 0.10.
- **Recovery (unbiasedness):** known effects recovered with bias < 0.003
  (push 0.3/0.6/1.0 → true ATE 0.078/0.196/0.418; mean estimates within 0.003).
- **Validity:** under H0 the within-subject condition labels are exchangeable, so the
  within-subject permutation is a valid exact randomization test; the subject is the
  correct cluster unit. No anti-conservative mechanism; the two-sided |T| p-value vs a
  one-sided ATE>0 alternative is conservative.
- **Independent REVIEWER reproduction: CALIBRATION PASS** (reproduced from a clean
  process, pod script MD5-verified).
- **Note:** the implementation is a two-sided test; the confirmatory protocol is
  two-sided at α=0.05 (type-I ≈ 0.047). If a one-sided test were used, type-I ≈ 0.025
  (conservative). The protocol wording and the implementation agree (two-sided).

## 4. Secondary analyses (predefined, EXPLORATORY)

- **Hypothesis-generating; CANNOT rescue a null primary or select a significant
  horizon/outcome after the fact.** Only the primary family {ATE_GENERAL, ATE_CUE} at the
  frozen `h*` supports a causal-redirection claim.
- Divergence, redirection latency, persistence horizon, return probability, effect decay
  (per-horizon); SHAM vs CONTROL (H3); endogenous-vs-exogenous (only if both H1 and H2
  significant); subjective effort / success awareness (descriptive + separate models).

## 5. Multiple-comparisons policy

- Primary family {ATE_GENERAL, ATE_CUE} (2 tests): Benjamini-Hochberg FDR at q = 0.05.
- Secondary outcomes are hypothesis-generating; not used to rescue a null primary.
- **No horizon fishing:** the primary is at the single frozen `h*`; per-horizon results are
  secondary and must not be used to select a "significant" horizon after the fact.

## 6. Exclusions and handling (frozen BEFORE outcome inspection)

- A trial is excluded only for a pre-specified technical failure (capture dropout, a window
  with < N_min valid embeddings), defined before any outcome is seen.
- No outcome-based exclusion. Intent-to-treat: all randomized trials analyzed, condition
  as-assigned.
- A subject is retained if ≥ 16 of 24 trials are valid (threshold frozen before outcomes).

## 7. Sample size

- N = 20 completed subjects (recruit 25 at 20% attrition), 24 trials/subject, from
  `data/scripts/cm8_power.py` (ICC≈0.2, ~80% power for Δ≈0.11 at α=0.05). The
  minimally-interesting effect (Δ≈0.11 in BRP) is justified a priori.

## 8. Frozen parameters (sealed at preregistration)

- Predictor θ (frozen) + its held-out calibration set (same capture modality).
- Basin tail (0.10) and the resulting `r_α`.
- Primary horizon `h*`.
- Cue-echo semantic-similarity threshold.
- Reference arm (pooled CONTROL/SHAM; SHAM-alone sensitivity).
- Randomization seed + manifest.
- Exclusion criteria + minimum-valid-trials threshold (16/24).
- Test level (two-sided α = 0.05), B = 10,000.

## 9. Decision rules

- `CM8_PASS_CAUSAL_TRAJECTORY_REDIRECTION`: H1 and/or H2 significant, sham no-op (H3),
  persistence beyond one step (H4), trivial-success guard satisfied.
- `CM8_PASS_EXOGENOUS_ONLY`: only H2 significant.
- `CM8_NULL_NO_REDIRECTION`: no significant ATE (a valid null).
- `CM8_BLOCK`: a gate fails (sham not a no-op, leakage, integrity).
