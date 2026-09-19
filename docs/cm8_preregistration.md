# CM-8F — Preregistration + Statistical Analysis Plan (DRAFT)

- **Status:** DRAFT for red-team. To be sealed (hash) before the confirmatory experiment.
- **Primary endpoint:** BRP at the frozen horizon `h*` (see `docs/cm8_basins_brp.md`).

## 1. Hypotheses

- **H1 (endogenous):** `ATE_GENERAL > 0` — a deliberate "move your thinking away"
  instruction increases the probability that the subsequent trajectory leaves the
  predicted semantic basin, relative to CONTROL/SHAM.
- **H2 (exogenous):** `ATE_CUE > 0` — an external semantic cue increases BRP relative to
  CONTROL/SHAM.
- **H3 (sham no-op):** SHAM ≈ CONTROL (the sham does not itself shift the trajectory).
- **H4 (persistence):** any redirection persists beyond the immediate one-step (persistence
  horizon ≥ 2), and is not explained by cue repetition (trivial-success guard).

## 2. Primary analysis

- **Estimands:** `ATE_GENERAL` and `ATE_CUE` (BRP difference vs the pooled CONTROL/SHAM
  reference), estimated **separately**. Pre-specified sensitivity: the same ATEs vs the
  **SHAM-alone** reference (isolates the redirection content from the prompt/interruption).
  If the pre-specified H3 (SHAM vs CONTROL) is significant, the SHAM-alone reference is the
  primary (the pooled reference is then a sensitivity).
- **Inference:** subject-clustered permutation test (permute condition labels within
  subjects; B = 10,000 in the confirmatory analysis; validated in
  `data/scripts/cm8_synthetic.py`). Two-sided, α = 0.05.
- **Primary horizon:** `h*` frozen at seal (target 2). The continuous basin distance
  `D(t, h*)` is a secondary (finer-grained) outcome with the same inference.
- **No post-treatment conditioning:** the primary ATE is NOT conditioned on effort,
  perceived success, or any other post-intervention variable.

## 3. Secondary analyses (predefined, EXPLORATORY)

- **These are hypothesis-generating and CANNOT be used to rescue a null primary or to
  select a "significant" horizon/outcome after the fact.** Only the primary family
  ({ATE_GENERAL, ATE_CUE} at the frozen `h*`) supports a causal-redirection claim.
- Divergence, redirection latency, persistence horizon, return probability, effect decay
  (per-horizon) — each with the same clustered inference, reported descriptively.
- SHAM vs CONTROL (confirm the sham no-op, H3).
- Endogenous vs exogenous comparison (only if both H1 and H2 are significant).
- Heterogeneous treatment effects (e.g., by a brief control-capacity measure) —
  exploratory, labeled as such.
- Subjective effort / success awareness — descriptive + separate models, never in the
  primary ATE.

## 4. Multiple-comparisons policy

- The **primary** family is {ATE_GENERAL, ATE_CUE} (2 tests). A Benjamini-Hochberg FDR
  control at q = 0.05 is applied to the primary family. Secondary outcomes are
  hypothesis-generating unless individually pre-specified; they are not used to rescue a
  null primary.
- **No horizon fishing:** the primary is at the single frozen `h*`. Per-horizon results are
  secondary and must not be used to select a "significant" horizon after the fact.

## 5. Exclusions and handling (frozen BEFORE outcome inspection)

- A trial is excluded only for a **pre-specified** technical failure (e.g., capture
  dropout, a thought window with < N_min valid embeddings), defined before any outcome is
  seen.
- No exclusion based on the outcome (BRP, latency, etc.).
- Intent-to-treat: all randomized trials are analyzed; the condition as-assigned is the
  analysis unit (no per-protocol reassignment).
- A minimum number of valid trials per subject (e.g., ≥ 16 of 24) is required for a
  subject to be retained; this threshold is frozen before outcomes.

## 6. Sample size

- N = 20 completed subjects (recruit 25 at 20% attrition), 24 trials/subject, from
  `data/scripts/cm8_power.py` (ICC≈0.2, ~80% power for Δ≈0.11 at α=0.05).
- The minimally-interesting effect (Δ≈0.11 in BRP) is justified a priori.

## 7. Frozen parameters (sealed at preregistration)

- Predictor `θ` (G8) + its held-out calibration set.
- Basin tail `α` (0.10) and the resulting radius `r_α`.
- Primary horizon `h*`.
- Cue-echo lexical-overlap rule.
- Reference arm (pooled CONTROL/SHAM).
- Randomization seed + manifest (G3).
- Exclusion criteria + minimum-valid-trials threshold.

## 8. Decision rules

- `CM8_PASS_CAUSAL_TRAJECTORY_REDIRECTION`: H1 and/or H2 significant, sham no-op (H3),
  persistence beyond one-step (H4), trivial-success guard satisfied.
- `CM8_PASS_EXOGENOUS_ONLY`: only H2 significant (external cue works; voluntary
  redirection not yet shown).
- `CM8_NULL_NO_REDIRECTION`: no significant ATE (a valid null).
- `CM8_BLOCK`: a gate fails (sham not a no-op, leakage, integrity).
