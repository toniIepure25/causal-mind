"""Multi-horizon prospective sample construction (CM-3B).

Extends CM-2's single-step samples to arbitrary future horizon h:
    history [t-k+1 .. t]  ->  target T[t+h]

Two horizon notions, both leakage-safe (history strictly before the target):
* event horizon h  : target is the h-th thought after the anchor t.
* time horizon dt  : target is the first thought whose start_time >=
                     anchor_start + dt (seconds).

HARD RULES (enforced + tested):
* every history index is strictly < target_index;
* the target's own features are never used as input;
* history and target come from the SAME subject;
* no held-out (val/test) statistics are used as features.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from causal_mind.thought.state_v1 import ThoughtState


@dataclass
class HorizonSample:
    subject: str
    anchor_index: int          # t (last history thought)
    h: int                     # event horizon (thoughts ahead)
    history: list[int] = field(default_factory=list)  # t-k+1 .. t
    target_index: int = -1     # t+h
    k: int = 1
    dt: float | None = None    # seconds, for time-horizon samples

    @property
    def is_prospective(self) -> bool:
        return len(self.history) > 0 and max(self.history) < self.target_index


def build_horizon_samples(states: list[ThoughtState], k: int, h: int) -> list[HorizonSample]:
    """Event-horizon samples: history [t-k+1..t] -> T[t+h]."""
    n = len(states)
    out: list[HorizonSample] = []
    for t in range(k - 1, n - h):  # need t >= k-1 (history) and t+h < n (target)
        hist = list(range(t - k + 1, t + 1))
        out.append(HorizonSample(subject=states[0].subject, anchor_index=t, h=h,
                                 history=hist, target_index=t + h, k=k))
    return out


def build_time_horizon_samples(states: list[ThoughtState], k: int, dt: float) -> list[HorizonSample]:
    """Time-horizon samples: history [t-k+1..t] -> first thought starting >= t_start + dt."""
    n = len(states)
    starts = [s.onset for s in states]
    out: list[HorizonSample] = []
    for t in range(k - 1, n):
        target_t = starts[t] + dt
        # first index j > t with start >= target_t
        j = t + 1
        while j < n and starts[j] < target_t:
            j += 1
        if j >= n:
            continue  # no thought that far ahead in this scan
        hist = list(range(t - k + 1, t + 1))
        out.append(HorizonSample(subject=states[0].subject, anchor_index=t, h=j - t,
                                 history=hist, target_index=j, k=k, dt=dt))
    return out


def assert_no_leakage(sample: HorizonSample, states: list[ThoughtState]) -> None:
    n = len(states)
    if not (0 <= sample.target_index < n):
        raise ValueError("target index out of range")
    if not sample.is_prospective:
        raise ValueError("history not strictly before target (future leakage)")
    for i in sample.history:
        if i >= sample.target_index:
            raise ValueError(f"history {i} >= target {sample.target_index}")
        if states[i].subject != sample.subject:
            raise ValueError("cross-subject history")
    if states[sample.target_index].subject != sample.subject:
        raise ValueError("target subject mismatch")


def all_samples_leakage_free(samples: list[HorizonSample],
                             states_by_subject: dict[str, list[ThoughtState]]) -> None:
    for s in samples:
        assert_no_leakage(s, states_by_subject[s.subject])
