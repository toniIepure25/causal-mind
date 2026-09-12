"""Linear multi-horizon transition model (CM-3E, primary).

One ridge map per horizon h: history window (k x dim) -> T[t+h] embedding (dim).
This is the direct-horizon model (Task 1): it predicts T[t+h] directly from the
history at t, so accumulated autoregressive error is NOT a confound.
"""
from __future__ import annotations

import numpy as np

from causal_mind.thought.multihorizon import HorizonSample
from causal_mind.thought.state_v1 import ThoughtState


def build_xy_h(samples: list[HorizonSample],
               states_by_subject: dict[str, list[ThoughtState]]):
    Xs, Ys = [], []
    for s in samples:
        st = states_by_subject[s.subject]
        Xs.append(np.concatenate([st[i].embedding for i in s.history]))
        Ys.append(st[s.target_index].embedding)
    return np.vstack(Xs), np.vstack(Ys)


class LinearMultiHorizon:
    name = "linear_multi_horizon"

    def __init__(self, k: int = 1, alpha: float = 100.0,
                 horizons: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 8, 10)) -> None:
        self.k, self.alpha = k, alpha
        self.horizons = horizons
        self._ridges: dict[int, object] = {}

    def fit(self, samples_by_h: dict[int, list[HorizonSample]],
            states_by_subject: dict[str, list[ThoughtState]]) -> LinearMultiHorizon:
        from sklearn.linear_model import Ridge
        for h in self.horizons:
            X, Y = build_xy_h(samples_by_h[h], states_by_subject)
            self._ridges[h] = Ridge(alpha=self.alpha).fit(X, Y)
        return self

    def predict(self, sample: HorizonSample, states: list[ThoughtState]) -> np.ndarray:
        x = np.concatenate([states[i].embedding for i in sample.history])
        return self._ridges[sample.h].predict(x.reshape(1, -1))[0]

    def param_count(self) -> int:
        return int(sum(int(r.coef_.size + r.intercept_.size) for r in self._ridges.values()))
