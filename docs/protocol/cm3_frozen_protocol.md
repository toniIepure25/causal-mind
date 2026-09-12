# CM-3 Frozen Protocol — Multi-Step Cognitive Futures

**Status:** FROZEN + SEALED before any decisive multi-step outcome.
**Anchor:** CM-2 provenance anchor commit `a0a701a`.
**Core question:** How far into the future does current cognitive history contain
meaningful information about subsequent thought trajectories?

## 1. Split (preserved from CM-2)

The CM-2 subject-disjoint split is **preserved unchanged**: 83/18/17
(train/val/test), CM-2 seal `675052618750ea7f780c566230c47baabb983955b28bc35f49fe58d6c0408668`.
No new subjects added/dropped; no re-split.

## 2. Frozen horizons

**Event horizons** (thoughts ahead): `h = 1, 2, 3, 4, 5, 6, 8, 10`.
All 118 subjects have enough thoughts for every horizon (samples 6318 → 5256).

**Time horizons** (seconds ahead): `Δt = 30, 60, 120, 180` s. Target = the first
thought whose `start_time >= t_anchor + Δt`. (Scan ≈ 600 s; ~11.5 s/thought median.)

Horizons are fixed. **No horizon is added, dropped, or tuned after seeing test
performance.**

## 3. Frozen targets (each with provenance)

| Target | Metric | Provenance |
|---|---|---|
| semantic | cosine(pred emb, actual emb) | model-inferred (frozen MiniLM) |
| topic | accuracy | directly observed (OSF prompt) |
| category | accuracy | directly observed (OSF 1-5) |
| psychological (per dim) | Pearson r | model-inferred (GPT) — secondary, never ground truth |
| trajectory direction | cosine(Δemb_pred, Δemb_actual) | derived (deterministic) |

## 4. Frozen candidate models (progressive; simple first)

1. **Linear multi-horizon transition** (primary): one ridge map per horizon,
   history window k → T[t+h] directly.
2. Regularized state-space model (only if #1 leaves headroom).
3. Direct horizon-specific predictors (subsumed by #1's per-horizon maps).
4. Compact recurrent (only if warranted).
5. Compact Transformer/SSM (only if #1-4 leave demonstrable headroom).

Any complex model must beat the linear model on frozen held-out data to be kept.

## 5. Frozen baselines (extended to h>1)

B0 marginal future · B1 current-state persistence · B2 Markov iterated h steps ·
B3 empirical k-history transition · B4 semantic persistence/drift ·
B5 nearest-neighbour trajectory continuation · B6 population-average trajectory ·
B7 strong frozen language-history · **CM-2 linear transition (central baseline).**

## 6. Primary object — Predictive Gain curve

`PredictiveGain(h) = Model(h) − StrongBaseline(h)`, with subject-level bootstrap
CIs at every horizon. StrongBaseline = the best of the frozen baselines at that h.

## 7. Thought Predictive Horizon (TPH) — prospective definition

`TPH_dim` = the maximum horizon h for which ALL hold:
1. `PredictiveGain(h) > 0`;
2. subject-level 95% CI of the gain excludes 0;
3. survives the frozen permutation/transition-destroyed null;
4. not driven by a small number of subjects (≥ 60% of test subjects above
   baseline);
5. red-team finds no leakage explanation.

Reported separately: `TPH_semantic`, `TPH_topic`, `TPH_psychological`.
**TPH is NOT chosen retrospectively to maximize the headline.**

## 8. Decision gates

- **C1 MULTI-STEP SIGNAL:** ≥1 dimension predictably above strong baseline beyond h=1.
- **C2 ROBUSTNESS:** survives subject-disjoint eval + frozen nulls.
- **C3 HORIZON CHARACTERIZED:** a defensible TPH or null boundary is estimated.
- **C4 COMPLEXITY JUSTIFIED:** any nonlinear/deep model shows held-out gain over linear.
- **C5 RED TEAM:** no unresolved artifact explains the future signal.

## 9. Nulls (frozen)

- **Time-shuffled:** permute each subject's target order (destroys temporal
  correspondence, preserves marginals).
- **Transition-destroyed:** replace each history with a random same-subject
  history of the same length.
- Per-horizon p-values; a distant-future result is not accepted until both nulls
  reject.
