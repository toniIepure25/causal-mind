# CAUSAL MIND — Limitations

A complete, honest list of limitations across the program. Part of the
`cm8-prehuman-v1.0` freeze. These are reported as limitations, not hidden.

## Prediction (CM-2 / CM-3, Paper 1)

- **Modest effect size.** The held-out semantic cosine is ~0.36 and the gain over the
  strongest baseline is ~0.03–0.04 at h=1, decaying to ~0.004 at h=10. The signal is real
  but small.
- **Small test set.** The sealed test split has **n=17 subjects**. The CIs are tight, but
  the absolute evidence base is small.
- **Semantic arm only.** The category (non-semantic) arm is **unvalidated**.
- **Single corpus.** The result is on one public thought-diary corpus (OSF `a56rm`);
  cross-corpus / cross-task generalization is not established.
- **Frozen, simple model.** A ridge multi-horizon model is used deliberately (reproducible,
  interpretable). It may not be the best possible model; the claim is the *signal*, not the
  model's ceiling.
- **TPH is a lower bound.** The gain is still significant at h=10, so the Thought Predictive
  Horizon is **≥ ~10 thoughts (~2 min)**, not an exact value.

## Neural (CM-5)

- **Null is conditional.** The "no incremental neural value" result is conditional on the
  frozen baseline, the HRF-safe window [onset−21s, onset−6s], the horizons (1,3,5,10), and
  this dataset. It does not rule out neural value under other windows/horizons/tasks.
- **Capacity ladder.** The result holds across the N1/N2/N3 capacity ladder, but the
  detection thresholds differ (~0.005 / ~0.02 / ~0.11 cosine); very small effects could be
  missed at higher capacities.

## Causal identification (CM-6)

- **Observational only.** The 0/84-identifiable result is for the *observational* thought
  stream. It motivates a randomized design; it is not a claim that no causal structure
  exists.
- **Unmeasured confounding.** The non-identifiability is driven by unmeasured confounding
  (incl. the per-subject rating baseline); measuring more covariates could change the
  identifiability set.

## Causal method validation (CM-7)

- **Clinical iEEG population.** The validation is on a clinical (epilepsy) iEEG population;
  generalization to healthy populations is not established.
- **No sham control.** The public dataset has no sham; the within-list randomization is the
  identification strategy.
- **Retrieved, not free, semantic state.** The outcome is a retrieved (cued) semantic state,
  not a free thought state.
- **Truncated sessions.** 14/26 sessions were truncated (recording ended early); this does
  not bias the within-list ATE but limits the total data.
- **Null effect.** The specific effect is a small, non-significant null; a small negative
  effect (down to ~−0.079) is not excluded.

## Confirmatory design (CM-8, Paper 3)

- **Not yet run.** The confirmatory human experiment is **designed and frozen but not run**
  (blocked on ethics + pilot). No human result exists yet.
- **Under-powered for small effects.** N=20 is under-powered for small effects (documented
  on the power surface). A null could be under-power, not a true null.
- **BRP failure modes.** The BRP has known failure modes (magnitude-only change, lexical
  echo, tiny-basin miscalibration, volatility); 7/9 adversarial cases produce a misleading
  high BRP. Secondary diagnostics are reported alongside; BRP stays PRIMARY.
- **Endogenous vs. exogenous.** The GENERAL-REDIRECT (endogenous) and SPECIFIC-CUE
  (exogenous) conditions are not perfectly clean; the CUE effect is partly a lexical echo
  (disclosed as confounded/secondary).
- **Fixed randomization is predictable.** The fixed counterbalanced permutation is
  predictable by design; blinding is the mitigation.

## Oracle lab (CM-9A)

- **Synthetic only.** The agent is a mean-reverting system with known parameters; no claim
  about real human thought.
- **No free-will claim.** The oracle is a formal object; the lab studies prediction vs.
  intervention, not consciousness.

## General

- **No free-will claim** is made or implied anywhere in the program.
- **No causal claim** is made from the observational data.
- **No claim** that the (null) public-intervention effect is real.
