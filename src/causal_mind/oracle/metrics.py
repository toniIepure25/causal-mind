"""CM-9A: metrics for the synthetic Oracle lab.

The agent has a SELF-PREDICTOR (a linear model that predicts its own next thought
from the last k thoughts). The oracle's intervention changes the thought stream, and
we measure how it changes the agent's ability to predict its own future:

  RPR (Recursive Prediction Ratio) = self-prediction error (oracle) /
                                     self-prediction error (baseline, no oracle).
      RPR < 1 -> the oracle makes the agent's future MORE predictable.
      RPR > 1 -> the oracle makes the agent's future LESS predictable.

  PIE (Prediction Intervention Effect) = self-prediction error (oracle) -
                                         self-prediction error (baseline).
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge


def self_prediction_error(states: np.ndarray, k: int = 3, alpha: float = 1.0) -> float:
    """Fit a linear self-predictor (state[t] ~ last k states) and return the mean
    prediction error (RMSE) over the held-out tail."""
    n = len(states)
    if n < k + 5:
        return float("nan")
    X, Y = [], []
    for t in range(k - 1, n - 1):
        X.append(np.concatenate(states[t - k + 1: t + 1]))
        Y.append(states[t + 1])
    X = np.array(X)
    Y = np.array(Y)
    # hold out the last 20% for evaluation
    n_eval = max(1, int(0.2 * len(X)))
    model = Ridge(alpha=alpha).fit(X[:-n_eval], Y[:-n_eval])
    pred = model.predict(X[-n_eval:])
    return float(np.sqrt(np.mean(np.sum((pred - Y[-n_eval:]) ** 2, axis=1))))


def rpr(error_oracle: float, error_baseline: float) -> float:
    if error_baseline <= 0 or not np.isfinite(error_baseline):
        return float("nan")
    return error_oracle / error_baseline


def pie(error_oracle: float, error_baseline: float) -> float:
    return error_oracle - error_baseline
