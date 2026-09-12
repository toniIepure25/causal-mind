# CM-3 Red-Team Review — MULTI-STEP COGNITIVE FUTURES

**Verdict: GO** (with noted limitations). Anchor commit `1784860`.

## 1. Leakage audit (first, per AGENTS.md)

| Check | Result |
|---|---|
| History strictly before target | PASS — `assert_no_leakage` enforces `max(history) < target_index`; tested. |
| Subject-disjoint split | PASS — CM-2 split (83/18/17) preserved, seal `67505261…` verified at runtime. |
| No val/test statistics as features | PASS — model + baselines use only TRAIN corpus + the sample's own past history. |
| Target features not used as input | PASS — model input is the history window only; target used solely as the label. |
| Baseline selection on test? | PASS — strongest baseline selected on **VAL**, final gain on TEST (no test-tuning). |

## 2. Reproducibility

Re-ran the full evaluation in a clean process. **Exact match** at every horizon
(h=1..10 model scores, baseline scores, gains, and CIs identical to the original).

## 3. Null adequacy

The frozen nulls (time-shuffled, transition-destroyed) both reject (p=0.0), but the
separation looked small (~0.005). A **stronger random-target null** (replace each
target with a random thought from the test pool, 300 iterations) was run:

| h | observed | null mean | null max | p | separation |
|---|---|---|---|---|---|
| 3 | 0.3303 | 0.3041 | 0.3140 | 0.0000 | +0.0262 |
| 5 | 0.3223 | 0.3061 | 0.3158 | 0.0000 | +0.0163 |

The observed prediction exceeds the **maximum** null sample at both horizons. The
future signal is not an artifact of the embedding space or the marginal.

## 4. Baseline strength

At h>1 the strongest frozen baseline is B0_marginal_future (the mean future), tied
with B6. The model beats it by +0.004..+0.026 and also beats the retrieval baselines
(B5, B3), which are stronger at h=1. The gain is against the best available baseline.

## 5. Limitations (must be stated, not hidden)

1. **Small test set (n=17 subjects).** The subject-level bootstrap CI is the honest
   unit but is based on 17 resampled subjects; CIs are correspondingly wide. Gains
   still exclude 0 at every horizon despite this.
2. **TPH is a lower bound.** The gain is still positive and significant at h=10 (the
   max tested horizon), so `TPH_semantic >= 10` thoughts (~2 min), not exactly 10.
3. **Overlapping windows.** Consecutive test anchors share history; the per-subject
   mean averages correlated samples. The subject-level CI preserves this correlation,
   but the effective independent unit is the subject, not the sample.
4. **Topic target is weak.** 2111 fine-grained topics make exact-match accuracy low
   (0.044 at h=1); the semantic and category targets carry the signal.
5. **Event vs time horizon.** The FPC is in event-horizon space; the time-horizon
   analysis (dt=30..180s) confirms the gain decays to ~0 by 180s, so the result is
   not an artifact of variable thought duration.

## 6. Decision

No leakage, reproducible, robust to a strong null, honest baseline comparison. The
multi-step signal is real. **GO** — report `TPH_semantic >= 10` with the limitations
above stated.
