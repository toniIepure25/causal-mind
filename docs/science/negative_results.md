# CAUSAL MIND — Negative Results

A negative result is a result. This document records every negative/null result in the
program, with its exact value, why it is a valid null (not an artifact), and what it rules
in/out. Part of the `cm8-prehuman-v1.0` freeze. **None of these are reopened to obtain a
positive.**

## 1. CM-5 — No incremental neural value for thought content (clean null)

- **Claim (C-005, L5, negative):** HRF-safe fMRI BOLD contains **no** incremental predictive
  value for target-thought content beyond the frozen behavioral-history model +
  motion/speech nuisance regressors.
- **Exact value:** IncrementalNeuralGain (M4−M2), primary N2/Schaefer-400 = **−0.088 /
  −0.085 / −0.085 / −0.090** at h=1/3/5/10; 95% CIs exclude 0; **0/16** test subjects
  positive; permutation p = **1.0**; Cohen's d = −2.51.
- **Why it's a valid null:** the negative gain is replicated by all negative controls
  (NC1 subject-perm, NC2 temporal-shift, NC3 block-perm, NC5 neural-randomize); NC4
  (nuisance-only) → 0 (no hidden shortcut); robust to motion-screen sensitivity. The gain is
  *negative* (neural features hurt), not just non-significant.
- **Rules out:** the hypothesis that HRF-safe brain activity extends the behavioral
  predictive horizon for thought content in this task/window/horizons.
- **Rules in:** nothing causal; the null is conditional on the frozen baseline, window,
  horizons, and dataset.

## 2. CM-6 — No causally identifiable edges in the observational thought stream

- **Claim (C-006/C-009, L5/L0, negative identification):** the observational thought
  dynamics are **not** causally identifiable.
- **Exact value:** **0 of 84** candidate lagged edges are identifiable (analysis_7); every
  backdoor-blocking set requires ≥1 unobserved node (unmeasured confounding, incl. the
  per-subject GPT-rating baseline). 39/272 CI edges survive BH-FDR; 0/126 mediator triples
  survive.
- **Why it's a valid result:** the identifiability audit is a formal check (do any
  backdoor-blocking sets exist using only observed nodes?); the answer is no.
- **Rules out:** any causal claim from the observational thought stream.
- **Rules in:** the confirmatory step must be a *randomized* experiment (not observational).

## 3. CM-7 — The public-intervention effect is a null (the method is validated)

- **Claim (C-010, L6, method validated; null effect):** on ds005494, the site-specific ATE
  of open-loop hippocampal/entorhinal stimulation at encoding on subsequent cued recall is a
  **small, non-significant null**.
- **Exact value:** ATE = **−0.0386**; exact two-phase randomization p = **0.0733** (20-subset
  robustness p=0.0754); list-level 95% CI **[−0.079, 0.002]**; subject-level [−0.087, 0.011].
- **Why it's a valid null:** integrity 3328/3330 (99.94%); 0 x-precedes-y violations; 0
  missing outcomes; destructive controls NC1/NC2/NC4 ≈ 0 (the machinery does not hallucinate
  effects); leakage audit PASS; serial-position confound canceled by balanced phase.
- **Rules out:** a positive effect of this stimulation on this outcome (positive effects are
  ruled out; a small negative effect down to ~−0.079 is not excluded).
- **Rules in:** the **method** is validated as a causal-inference instrument (the point of
  CM-7). No claim that stimulation enhances memory.

## 4. CM-8R — The BRP has known failure modes (disclosed, not hidden)

- **Claim (part of C-011, L0):** the frozen BRP is a valid PRIMARY estimand but has known
  failure modes.
- **Exact value:** in the BRP red team, **7 of 9** adversarial cases produce a misleading
  high BRP (magnitude-only change, lexical echo, tiny-basin miscalibration, volatility).
- **Why it's disclosed:** the secondary diagnostics (cosine-direction change, Mahalanobis
  distance, persistence, semantic novelty, AUC divergence) reveal each failure mode. BRP
  stays PRIMARY; the diagnostics are reported alongside.
- **Rules in:** the BRP must always be reported with its secondary diagnostics.

## How these negatives are used

- They are **reported as results** in the master summary, the evidence matrix, and the
  papers (Paper 1 §7, Paper 2 §2/§4, Paper 3 §8).
- They **constrain the claims** (no causal claim from observational data; the neural null
  is conditional; the CM-7 effect is a null).
- They are **not reopened** to obtain a positive. A negative result is a result.
