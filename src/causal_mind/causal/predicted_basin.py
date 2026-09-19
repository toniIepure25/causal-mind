"""Predicted-future semantic basin and BRP for CM-8 (Pre-Oracle).

Extends the CM-6 :class:`~causal_mind.causal.basin.SemanticBasin` to the CM-8
setting. The basin is a *prediction-interval* ball around the frozen predictor's
forecast, with a radius set at a held-out quantile of the predictor's error
norm. BRP is the probability that the observed future falls outside this basin.

Everything here is defined **prospectively**: the radius comes from a held-out
calibration of the predictor's error, never from the intervention outcomes.
See ``docs/cm8_basins_brp.md``.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _as_2d(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    return x


def fit_prediction_interval_radius(error_norms: np.ndarray, alpha: float = 0.10) -> float:
    """``r_alpha = Quantile_{1-alpha}`` of the held-out prediction-error norms.

    ``error_norms`` are ``||y_i(h) - f(H_i)(h)||`` on a held-out calibration set
    (no intervention data). The returned radius is the distance within which the
    predictor typically lands (covers ``1 - alpha`` of the error distribution).
    """
    r = np.asarray(error_norms, dtype=float)
    r = r[np.isfinite(r)]
    if len(r) == 0:
        raise ValueError("no finite calibration errors to fit the radius")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"alpha must be in (0,1), got {alpha}")
    return float(np.quantile(r, 1.0 - alpha))


@dataclass
class PredictedFutureBasin:
    """Ball around a single predicted point with a prediction-interval radius.

    Attributes
    ----------
    center:
        The predicted future point, shape ``(d,)``.
    radius:
        ``r_alpha`` (the prediction-interval radius).
    alpha:
        Tail probability; the radius covers ``1 - alpha`` of the error distribution.
    """

    center: np.ndarray
    radius: float
    alpha: float = 0.10

    def distance(self, x: np.ndarray) -> np.ndarray:
        """Euclidean distance from each embedding in ``x`` to the center."""
        return np.linalg.norm(_as_2d(x) - self.center, axis=1)

    def normalized_distance(self, x: np.ndarray) -> np.ndarray:
        """``D = distance / radius``; ``D > 1`` means outside the basin."""
        return self.distance(x) / self.radius

    def leave(self, x: np.ndarray) -> np.ndarray:
        """Binary leave indicator: 1 where the embedding is outside the basin."""
        return (self.normalized_distance(x) > 1.0).astype(int)

    def brp(self, x: np.ndarray) -> float:
        """BRP = fraction of ``x`` that leave the basin."""
        lv = self.leave(x)
        return float(lv.mean()) if len(lv) else 0.0


def predicted_brp(
    observed_futures: np.ndarray,
    predicted_points: np.ndarray,
    error_norms: np.ndarray,
    alpha: float = 0.10,
) -> dict:
    """BRP for the predicted-future basin, with per-trial predicted centers.

    Parameters
    ----------
    observed_futures:
        ``(n, d)`` observed post-intervention states at the frozen horizon.
    predicted_points:
        ``(n, d)`` the frozen predictor's forecast for each trial at that horizon.
    error_norms:
        held-out prediction-error norms used to calibrate the radius.
    alpha:
        tail probability for the radius (primary 0.10).

    Returns
    -------
    dict with ``brp``, ``radius``, ``leave`` (n,), ``normalized_distance`` (n,).
    """
    obs = _as_2d(observed_futures)
    pred = _as_2d(predicted_points)
    if obs.shape != pred.shape:
        raise ValueError(f"observed/predicted shape mismatch: {obs.shape} vs {pred.shape}")
    radius = fit_prediction_interval_radius(error_norms, alpha)
    dist = np.linalg.norm(obs - pred, axis=1)
    nd = dist / radius
    leave = (nd > 1.0).astype(int)
    brp = float(leave.mean()) if len(leave) else 0.0
    return {
        "brp": brp,
        "radius": radius,
        "leave": leave,
        "normalized_distance": nd,
        "n": int(len(leave)),
    }


def redirection_latency(leave_sequence: np.ndarray) -> int | None:
    """First horizon index (0-based) at which the trajectory leaves the basin.

    ``leave_sequence[h]`` is the leave indicator at horizon ``h``. Returns the
    first ``h`` with a leave, or ``None`` if the trajectory never leaves.
    """
    lv = np.asarray(leave_sequence, dtype=int)
    idx = np.where(lv == 1)[0]
    return int(idx[0]) if len(idx) else None


def persistence_horizon(leave_sequence: np.ndarray, start: int = 0) -> int:
    """Length of the contiguous leave-run beginning at ``start``.

    Counts how many consecutive horizons (from ``start``) the trajectory stays
    redirected (outside the basin). This is the Redirection Persistence Horizon.
    """
    lv = np.asarray(leave_sequence, dtype=int)
    if start >= len(lv):
        return 0
    run = 0
    for v in lv[start:]:
        if v == 1:
            run += 1
        else:
            break
    return run


def return_probability(leave_sequence: np.ndarray) -> float:
    """Fraction of leave-events that are followed by a re-entry into the basin.

    A "return" is a transition from leave (1) to inside (0). The return
    probability is the number of returns divided by the number of leaves that
    were followed by at least one inside step.
    """
    lv = np.asarray(leave_sequence, dtype=int)
    if len(lv) < 2:
        return 0.0
    leaves = (lv[:-1] == 1)
    returns = (lv[:-1] == 1) & (lv[1:] == 0)
    if leaves.sum() == 0:
        return 0.0
    return float(returns.sum() / leaves.sum())
