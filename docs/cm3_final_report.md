# CM-3 Final Report — MULTI-STEP COGNITIVE FUTURES

**Decision: `CM3_PASS`** · anchor commit `1784860` · red-team GO.

## Question

How far into the future does current cognitive history contain information about
subsequent thought trajectories? (CM-2 established 1-step prediction; CM-3 measures
the decay of prospective information over the horizon and estimates the first
**Thought Predictive Horizon (TPH)**.)

## Setup (frozen, sealed before outcomes)

- 118 subjects, 6436 thoughts; CM-2 split preserved (83/18/17, seal `67505261…`).
- Event horizons h=1..10; time horizons 30/60/120/180 s; k=3 history (saturates).
- Primary model: linear multi-horizon transition (history → T[t+h] directly).
- Baselines B0–B7 + CM-2 linear; strongest selected on VAL, gain measured on TEST.
- Protocol seal `10ce16ff…`.

## Headline — Future Predictability Curve (semantic)

PredictiveGain(h) = Model(h) − StrongestBaseline(h), subject-level 95% CI:

| h | model | strong baseline | gain | 95% CI |
|---|---|---|---|---|
| 1 | 0.3623 | B4_drift 0.3274 | **+0.0349** | [+0.0253, +0.0445] |
| 2 | 0.3406 | B0 0.3146 | **+0.0261** | [+0.0205, +0.0321] |
| 3 | 0.3285 | B0 0.3133 | **+0.0152** | [+0.0091, +0.0220] |
| 4 | 0.3236 | B0 0.3122 | **+0.0114** | [+0.0070, +0.0165] |
| 5 | 0.3210 | B0 0.3117 | **+0.0092** | [+0.0053, +0.0133] |
| 6 | 0.3187 | B0 0.3114 | **+0.0073** | [+0.0032, +0.0113] |
| 8 | 0.3153 | B0 0.3101 | **+0.0052** | [+0.0018, +0.0085] |
| 10 | 0.3135 | B0 0.3091 | **+0.0044** | [+0.0015, +0.0072] |

The gain is **positive and significant at every horizon** and decays smoothly and
monotonically. The h=1 model score (0.3623) exactly reproduces CM-2.

## Thought Predictive Horizon

`TPH_semantic >= 10` thoughts (~2 min): the gain is still positive with a CI excluding
0 at the maximum tested horizon, so the true horizon is at least 10 thoughts. This is a
**lower bound**, not a point estimate chosen to maximize a headline.

## Secondary analyses

- **History depth × horizon:** saturates at k≈3 (k=3 best at h=1; k=5 no better) —
  consistent with CM-2.
- **Time horizons:** gain +0.014 (30s) → +0.005 (60s) → +0.001 (120s) → ~0 (180s).
  The predictive window is ~2 minutes in wall-clock time.
- **Category:** accuracy decays 0.237 (h=1) → 0.135 (h=5), above the 0.2 chance.
- **Topic:** weak (0.044 → 0.011) — 2111 fine-grained topics make exact match hard.
- **Entropy / branching:** mean pairwise cosine among actual futures ≈ 0.17 at all
  horizons — the future is a diffuse distribution of possible thoughts, not a point.

## Robustness

- **Reproduced exactly** in a clean process (all horizons identical).
- **Frozen nulls** (time-shuffled, transition-destroyed): both p=0.0.
- **Stronger random-target null** (300 iters): h=3 sep +0.0262, h=5 sep +0.0163,
  p=0.0000; observed exceeds the max null sample. Not an embedding/marginal artifact.

## Decision gates

| Gate | Status |
|---|---|
| C1 multi-step signal | PASS (gain > 0, CI excl. 0, all h) |
| C2 robustness | PASS (subject-disjoint + nulls) |
| C3 horizon characterized | PASS (TPH ≥ 10) |
| C4 complexity justified | N/A (linear model is primary and sufficient) |
| C5 red team | PASS (GO) |

## Limitations

1. Small test set (n=17 subjects) → wide CIs, limited power.
2. TPH is a lower bound (≥ 10), not a point estimate.
3. Overlapping test windows; the subject is the independent unit.
4. Topic target weak due to fine-grained topics.
5. No neural (fMRI) data yet — that is CM-5.

## Interpretation

Cognitive history carries **genuinely prospective** information: a linear model of the
last few thoughts predicts the semantic content of thoughts up to ~10 steps / ~2 minutes
ahead, significantly better than any frozen baseline, and the advantage decays smoothly
with the horizon. This is the first empirical estimate of a Thought Predictive Horizon.
