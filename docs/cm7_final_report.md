# CM-7 — Final Report: Public Intervention Method Validation (ds005494)

- **Date:** 2026-09-17 · **Engine:** ORCHESTRATOR (CM-7)
- **Decision: `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT`**
- **Companions:** `docs/cm7_protocol.md` (frozen), `docs/cm7_identification.md`,
  `docs/datasets/ds005494_audit.md`, `reports/cm7_results.json`, `reports/cm7_results.md`,
  `data/scripts/cm7_analyze.py`, `data/manifests/ds005494_manifest.json`.

---

## 1. What CM-7 set out to do

Validate that the CAUSAL MIND intervention framework can correctly recover an
experimentally-identified causal effect `P(Y_future | do(X))` in an **independent public
dataset**, without overclaiming. This is a **method-validation** bridge (FORECAST →
INTERVENE). It is NOT a claim that "hippocampal stimulation enhances memory," and NOT a
claim about spontaneous-thought redirection or free will.

## 2. Dataset and design (from the authoritative audit)

- **ds005494** (Herrema & Kahana, CC0, v1.0.1): open-loop electrical stimulation of a single
  targeted hippocampal/entorhinal electrode at **encoding** (or retrieval) of paired-associate
  word pairs, with **cued recall** as the future outcome. N=20 subjects, 26 sessions.
- **Intervention (X):** the documented open-loop train (50 Hz, 230 pulses, 300 µs, 4.6 s,
  onset −200 ms) delivered to alternating pairs (3 of 6) in encoding-stim lists.
- **Outcome (Y):** cued recall of the pair (`correct` 0/1, `resp_word`, `response_time`).
- **Randomization:** list-level within-subject (10 enc-stim / 10 ret-stim / 5 no-stim per
  session; alternating phase randomized 50/50). This is what identifies the ATE.
- **Minimal acquisition:** 26/26 `beh.tsv` (no iEEG), 6.4 MB, SHA-256 manifest.

## 3. Primary result

**Estimand:** site-specific ATE of open-loop stimulation of the targeted electrode at
encoding on subsequent cued recall, pair-level within encoding-stim lists, aggregated across
subjects.

- **ATE = −0.0386** (stimulated pairs recalled slightly LESS than non-stimulated pairs).
- **Exact 2-phase randomization p = 0.0733** (20-subset robustness p = 0.0754) — NOT
  significant at α=0.05.
- **List-level bootstrap 95% CI = [−0.0787, 0.0015]**; **subject-level (nesting-aware)
  95% CI = [−0.0874, 0.0114]**. Both include 0.
- **counterfactual_status = `experimentally_identified`** (via the CM-6 engine with a valid
  `RandomizedEvidence` record). The estimand is identified by design; the estimate is ~0.
- **Corroborating list-level contrast** (enc-stim vs no-stim lists): −0.0080 (p=0.712) — null.
- **Distributional:** latency stim 2.764 s vs no-stim 2.668 s (p=0.163, null); correct-rate
  stim 0.350 vs no-stim 0.389; semantic CTE (MiniLM centroid distance) 0.046 (negligible
  relative to mean-pairwise 0.981) — no meaningful shift in recalled-word content.

**Reading:** the framework correctly identifies and estimates the causal effect, and the
effect is a **valid null** — a small, non-significant tendency for encoding stimulation to
reduce cued recall. The CI upper bound (≈0.002) rules out positive effects; a small negative
effect down to ≈−0.079 is not excluded.

## 4. Method validation (the point of CM-7)

The framework is **validated** as a causal-inference instrument:

- **Leakage audit (REVIEWER): PASS.** No post-treatment variable (iEEG, arousal,
  math-distractor performance, subjective state, seizure) enters the primary adjustment set —
  the primary uses only X (stimulation) and Y (correct). The retrieval-stim (concurrent)
  contrast is excluded from the primary future-state estimand. Inference clusters at the
  list/subject level, not the trial level.
- **Destructive / placebo controls (all ~0, as required):**
  - NC1 X-within-list permutation null mean = 0.0000 (the observed ATE sits in its tail only
    weakly, p=0.073).
  - NC2 Y-permutation mean = 0.0005.
  - NC4 no-intervention (fake X on retrieval-stim lists, which had NO encoding stimulation)
    mean = 0.0016.
  - The machinery does **not** hallucinate an effect when there is none.
- **Position-confound handled:** the alternating phase is balanced (start-on=109,
  start-off=107), so the serial-position confound cancels in the ATE. Decomposition:
  stimulation effect δ ≈ −0.038, serial-position effect (odd−even) ≈ −0.044; the phase
  imbalance term is −0.0004 (negligible).
- **Integrity:** 3328/3330 (99.94%) official `STUDY_PAIR` outcomes match a raw `REC_EVENT`
  attempt; 0 pairs with a missing official `correct`; the 2 unmatched pairs are documented
  (both official_correct=0). Repeated recall attempts (some pairs have 2 `REC_EVENT` rows) are
  handled by matching the official outcome to any attempt.
- **Reviewer verdict: GO-WITH-CHANGES** — all 4 requested changes applied (permutation-null
  CI + labeled list/subject CIs; decision-mapping bug fixed so failed controls → BLOCK;
  Y<0 count + mismatched-pair documentation; negative-effect caveat).

## 5. Data caveats (do not over-read the null)

- **Session truncation:** 14/26 sessions ended early (<25 lists; 555 total lists). This does
  not bias the primary within-list ATE (each encoding-stim list is a self-contained 3-vs-3
  contrast), and the encoding-stim list count (216) is not truncation-biased (222 expected,
  within 0.5 SD).
- **Clinical iEEG population** (inferred epilepsy-monitoring cohort); **no sham control** —
  the estimand is the total effect of the delivered train (neural + non-specific), site- and
  train-specific, population-limited.
- **Retrieved (cued) semantic state**, not a free thought state; the outcome is a narrow,
  well-defined recall event.

## 6. Claims boundary (even on a PASS, this is the ceiling)

Permitted: "the CAUSAL MIND intervention framework recovered and validated an
experimentally-identified causal effect — the site-specific effect of open-loop stimulation
of the targeted hippocampal/entorhinal electrode at encoding on subsequent cued recall — in
the independent public dataset ds005494; the estimated effect is a small, non-significant
reduction in recall (a valid null)."

NOT permitted: "hippocampal stimulation enhances/improves memory"; general mental causation;
causal redirection of spontaneous thought; free will; "THE ORACLE validated"; any claim that
the null is evidence that stimulation does nothing (a small negative effect is not excluded).

## 7. Decision and next step

- **Decision: `CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT`.** The method is validated (leakage
  audit PASS, destructive controls ~0, correct inference, correct engine labeling); the
  specific causal effect is a valid null.
- **Next major phase: CM-8 (Pre-Oracle / Break-the-Chain own experiment, IRB-gated)** — NOT
  THE ORACLE. CM-7 validated the machinery on public data; CM-8 is the first own experiment
  (E8 voluntary redirection) on the critical path to THE ORACLE.
