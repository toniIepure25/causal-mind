# CM-XVAL-1 Inference Adjudication

**Status:** `CMXVAL_PARTIAL_REPLICATION`
**Claim:** C-101 (revised; history preserved)
**Script:** `data/scripts/cm_xval_inference.py`
**Machine-readable:** `reports/cm_xval/cm_xval_inference.json`
**Dataset:** Open Play (openESM 0075_ballou), Zenodo 10.5281/zenodo.17536656, `displaced_activity`
**Split:** 473/101/102 subject-disjoint, seed 20260921, k=3, horizons 1/2/3/5/10

---

## 1. The apparent discrepancy

The original CM-XVAL-1 run reported two results that look contradictory:

| Procedure | Statistic | Result |
|---|---|---|
| Subject-level paired bootstrap (model − strongest baseline) | gain CI at h=1 | **+0.0164 [+0.0094, +0.0229]** → excludes 0 |
| Target-shuffle permutation (model vs random within-subject target) | p at h=1 | **0.71** → not significant |

A CI that excludes 0 alongside a p of 0.71 is not automatically a bug. The two
procedures test **different null hypotheses** and use **different resampling units**.
This document determines exactly what each tests, recomputes the inference at the
correct unit, and runs a predeclared family of destructive nulls.

## 2. Which null hypothesis each procedure tests

**Procedure A — subject-level paired bootstrap (the gain CI).**
For each test subject `s`, compute the per-subject mean cosine for the model and for
the strongest frozen baseline, then the paired difference `gain_s`. Resampling the
subjects tests:

> **H0(A): E_sub[score_model − score_baseline] = 0**

This is a **relative** test: does the model add value *over the best frozen baseline*?
Both the model and the baseline exploit within-person similarity; the test asks whether
the model does it measurably better. The unit is the **subject** (the correct
independent unit). This is the correct primary inference.

**Procedure B — target-shuffle permutation (the original p=0.71).**
For each test sample the model predicts from the subject's history, and the prediction's
cosine to the *actual* next entry is compared against its cosine to a *random entry of
the same subject*. This tests:

> **H0(B): the model's absolute prediction is no more similar to the actual next entry
> than to a random entry of the same person.**

This is an **absolute** test against a **within-subject marginal** null. Because a
subject's `displaced_activity` entries are mutually similar (high within-person
marginal, ~0.65), the null is *high*, so the model's absolute cosine (~0.65) does not
exceed it. Crucially, the original run computed the observed statistic at the **event
level (micro)** (0.6509) while the gain CI was at the **subject level (macro)**
(0.6414) — a unit mismatch that compounded the apparent contradiction.

**Reconciliation.** A and B are not competing estimates of the same quantity. A asks
"better than the baseline?"; B asks "better than a random entry of the same person?".
A can be true while B is false when the whole field (model *and* baselines) sits on top
of a high within-person marginal: everyone predicts "a typical entry for this person"
well, and the specific next-entry signal is small relative to that marginal.

## 3. Inference at the correct unit (subject-level)

All tests below use the **subject** as the unit of inference. Event-level numbers are
reported only as descriptive secondary analysis.

| h | N subj | N events | gain mean | gain CI (paired boot) | sign test p | subject perm p | prop positive | Cohen's d |
|---|---|---|---|---|---|---|---|---|
| 1 | 102 | 1132 | +0.0164 | [+0.0094, +0.0229] | 0.0000 | 0.0005 | 83/102 | 0.487 |
| 2 | 102 | 1132 | +0.0175 | [+0.0096, +0.0253] | 0.0002 | 0.0005 | 70/102 | 0.426 |
| 3 | 99 | 996 | +0.0339 | [+0.0144, +0.0508] | 0.0000 | 0.0005 | 70/99 | 0.357 |
| 5 | 85 | 710 | +0.0303 | [+0.0193, +0.0429] | 0.0000 | 0.0005 | 68/85 | 0.545 |
| 10 | 65 | 410 | +0.0177 | [+0.0082, +0.0271] | 0.0059 | 0.0015 | 44/65 | 0.448 |

Methods: (1) subject-level paired bootstrap (N_BOOT=2000); (2) two-sided sign test on
the per-subject gain; (3) subject-level sign-flip permutation (N=2000); (4)
hierarchical two-level bootstrap (resample subjects, then events within). The
subject-level advantage is **consistent and robust** across all horizons: the paired
bootstrap CI excludes 0 everywhere, the sign test is significant everywhere, and the
subject-level permutation is significant everywhere. The effect size is small-to-medium
(Cohen's d 0.36–0.55) and the proportion of positive subjects is 68–83/102.

Event-level (secondary, descriptive only): the event-level gain is positive at every
horizon but the events are **not independent** (they are repeated within a subject), so
event-level p-values would understate uncertainty and are not used for the decision.

## 4. Predeclared destructive-null family (primary horizon h=1)

Each null destroys a specific dependence and preserves others. The model prediction is
computed once from the correct history; only the target (and, for N5, the history) is
altered. p = fraction of null realizations with null cosine ≥ observed (observed 0.6509).
**All seven nulls are reported; the most favorable is not singled out.**

| Null | Destroys | Preserves | Null mean | p | Rejected? |
|---|---|---|---|---|---|
| **N0** across-subject target | subject identity + temporal link | marginal target dist. | 0.4951 | **0.0005** | **YES** |
| **N1** within-subject target | temporal alignment (next entry) | subject + marginal | 0.6530 | 0.6842 | no |
| **N2** circular temporal shift | specific temporal alignment | autocorrelation + subject + marginal | 0.6533 | 0.6932 | no |
| **N3** block shuffle (size k) | long-range temporal structure | short-range autocorr. + subject + marginal | 0.6527 | 0.7211 | no |
| **N4** history–target mismatch | specific history→target link | subject + marginal | 0.6488 | 0.3253 | no |
| **N5** wrong-subject history | subject-specificity of history | target subject + marginal | 0.4937 | **0.0005** | **YES** |
| **N6** transition-destroyed target | transition (history→immediate next) | subject + marginal | 0.6485 | 0.2959 | no |

**Reading the null family.**
- **N0 and N5 rejected (p=0.0005):** the model's prediction is far more similar to the
  *correct subject's* target than to a random subject's target (0.65 vs 0.495), and using
  the *subject's own* history is far better than another subject's history (0.65 vs
  0.494). The model **does** exploit subject identity.
- **N1, N2, N3, N4, N6 not rejected:** once subject identity is held fixed, the model
  does **not** beat a random entry of the same person, nor exploit the specific temporal
  alignment, long-range structure, the specific history→target link, or the immediate
  transition. The within-person marginal (~0.65) carries essentially all of the
  absolute signal.

## 5. Decision (per §28 revision rule)

- Subject-level model–baseline advantage **survives** appropriate subject-level
  inference (CI excludes 0; sign test and subject permutation significant at all
  horizons).
- The **temporal/transition-specific** destructive nulls (N1–N4, N6) are **not**
  rejected: the evidence for specific next-entry (temporal-semantic) prediction is
  ambiguous/absent on this dataset.

Therefore the decision is:

> **`CMXVAL_PARTIAL_REPLICATION`** — the model–baseline advantage exists at the correct
> unit, but the temporal/transition-specific evidence remains ambiguous.

This refines (does not contradict) the original `CMXVAL_PARTIAL`: the substance is the
same, the label is now precise, and the earlier "p=0.71 vs CI-excludes-0" tension is
explained as a null-hypothesis and unit mismatch, not a bug.

## 6. Scientific interpretation

The CM-2/CM-3 predictive-dynamics effect is **paradigm-dependent**. On the rich
thought-stream (ds006067) the specific next-thought prediction is strong. On this
domain-shifted, short, repetitive gaming-diary activity text, what transfers is a
**small, subject-specific, beats-the-baseline** advantage; the strong
**temporal-semantic** next-entry prediction does **not** transfer. This is a legitimate
and informative external-validation outcome: it bounds the generality of the effect
without overstating it.

## 7. What was NOT done (guardrails)

- No null was dropped to obtain a PASS; all seven predeclared nulls are reported.
- No test-set tuning; the model and baselines are fit on train only, evaluated on
  sealed test.
- No CM-8 protocol change; no human data; external public dataset only.
- The original `cm_xval_openplay.py` output is preserved; this adjudication is a new
  analysis (new script, new JSON) that supersedes the *inference* (not the data).
