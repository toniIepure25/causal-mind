"""Strict prospective sample construction (CM-2B).

A sample is:  history up to thought t  ->  predict thought t+1.
With window k:  history = thoughts [t-k+1 .. t]  ->  target = t+1.

HARD RULES (enforced + tested):
* every history index is strictly < target_index (no present/future);
* the target's own text/annotation/embedding is never a feature;
* history and target come from the SAME subject (no cross-subject mixing);
* no statistics computed over held-out (val/test) subjects are used as features.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from causal_mind.thought.state_v1 import ThoughtState


@dataclass
class Sample:
    subject: str
    target_index: int          # index of thought t+1
    history: list[int] = field(default_factory=list)  # indices t-k+1 .. t
    k: int = 1

    @property
    def is_prospective(self) -> bool:
        return len(self.history) > 0 and max(self.history) < self.target_index


def build_prospective_samples(states: list[ThoughtState], k: int = 1) -> list[Sample]:
    """For one subject's ordered states, build history->next samples with window k."""
    n = len(states)
    samples: list[Sample] = []
    for target in range(k, n):  # target = t+1, so t = target-1 >= k-1
        hist = list(range(target - k, target))  # t-k+1 .. t  (all < target)
        samples.append(Sample(subject=states[0].subject, target_index=target, history=hist, k=k))
    return samples


def history_matrix(sample: Sample, states: list[ThoughtState],
                   get_feat) -> np.ndarray:
    """Feature rows for a sample's history (order preserved, oldest -> newest)."""
    return np.vstack([get_feat(states[i]) for i in sample.history])


def assert_no_leakage(sample: Sample, states: list[ThoughtState]) -> None:
    """Raise if a sample violates any prospective rule."""
    n = len(states)
    if not (0 <= sample.target_index < n):
        raise ValueError("target index out of range")
    if not sample.is_prospective:
        raise ValueError("history not strictly before target (future leakage)")
    for i in sample.history:
        if i >= sample.target_index:
            raise ValueError(f"history index {i} >= target {sample.target_index}")
        if states[i].subject != sample.subject:
            raise ValueError("cross-subject history")
    if states[sample.target_index].subject != sample.subject:
        raise ValueError("target subject mismatch")


def all_samples_leakage_free(
    samples: list[Sample], states_by_subject: dict[str, list[ThoughtState]]
) -> None:
    for s in samples:
        assert_no_leakage(s, states_by_subject[s.subject])
