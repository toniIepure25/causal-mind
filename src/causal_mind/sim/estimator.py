"""CM-8R3: the CM-8 primary estimator (ATE + subject-clustered permutation test).

Mirrors the frozen confirmatory analysis: ATE = mean(leave | arm) - mean(leave |
pooled control/sham), tested with a within-subject (subject-clustered) permutation
test, two-sided, at the confirmatory test level. The reference arm is pooled
CONTROL/SHAM (the SHAM-alone sensitivity is a separate contrast).
"""
from __future__ import annotations

import numpy as np

from causal_mind.sim.world import TrialRecord


def _arrays(recs: list[TrialRecord]):
    recs = [r for r in recs if r.leave >= 0]  # drop MNAR-missing trials
    subjects = np.array([r.subject for r in recs])
    conditions = np.array([r.condition for r in recs])
    leave = np.array([r.leave for r in recs], dtype=float)
    return subjects, conditions, leave


def _diff(conditions, leave, arm, ref=("control", "sham")) -> float:
    am = conditions == arm
    rm = np.isin(conditions, ref)
    if am.sum() == 0 or rm.sum() == 0:
        return 0.0
    return float(leave[am].mean() - leave[rm].mean())


def ate_and_p(recs: list[TrialRecord], arm: str, b_perm: int = 1000,
              ref=("control", "sham"), rng: np.random.Generator | None = None
              ) -> tuple[float, float]:
    """ATE (arm vs pooled control/sham) + subject-clustered permutation p-value."""
    rng = rng or np.random.default_rng(0)
    subjects, conditions, leave = _arrays(recs)
    ate = _diff(conditions, leave, arm, ref)
    groups = [np.where(subjects == s)[0] for s in np.unique(subjects)]
    null = np.empty(b_perm)
    for b in range(b_perm):
        perm = conditions.copy()
        for idx in groups:
            perm[idx] = rng.permutation(conditions[idx])
        null[b] = _diff(perm, leave, arm, ref)
    p = float(np.mean(np.abs(null) >= abs(ate)))
    return ate, p


def brp_by_condition(recs: list[TrialRecord]) -> dict[str, float]:
    subjects, conditions, leave = _arrays(recs)
    out = {}
    for c in ("control", "sham", "general", "cue"):
        m = conditions == c
        out[c] = float(leave[m].mean()) if m.sum() else 0.0
    return out
