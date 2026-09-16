"""Causal metrics in the thought-state (embedding) space.

Each metric is defined on sets of embedding vectors (shape ``(n, d)``) and is
intended to be read *relative to matched control transitions*: generic
embedding movement is not by itself meaningful, so every metric optionally
takes a matched ``control`` sample and reports the effect relative to it.
The baseline "semantic basin" is formalized by
:class:`causal_mind.causal.basin.SemanticBasin` and the matched control used
for calibration is drawn by :func:`sample_matched_controls`.

Metrics
-------
* ``causal_trajectory_effect``   -- CTE(X): distance between the future
  distribution under do(X=a) and under do(X=b).
* ``branch_redirection_probability`` -- BRP: P(future leaves the baseline
  semantic basin | do(intervention)).
* ``trajectory_persistence``     -- how much the future stays near the current state.
* ``trajectory_divergence``      -- how far two intervened branches drift apart.
* ``intervention_effect_decay``  -- decay of the intervention effect over horizon.
* ``trajectory_effect_over_horizon`` -- per-horizon effect vs a matched
  control sequence, with the fitted half-life as the value.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from causal_mind.causal.basin import SemanticBasin


def _as_2d(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    return x


def _centroid_distance(a: np.ndarray, b: np.ndarray) -> float:
    a, b = _as_2d(a), _as_2d(b)
    return float(np.linalg.norm(a.mean(axis=0) - b.mean(axis=0)))


def _mean_pairwise_distance(a: np.ndarray, b: np.ndarray) -> float:
    a, b = _as_2d(a), _as_2d(b)
    diff = a[:, None, :] - b[None, :, :]
    return float(np.linalg.norm(diff, axis=2).mean())


def _mean_cosine(a: np.ndarray, b: np.ndarray) -> float:
    a, b = _as_2d(a), _as_2d(b)
    a = a / np.linalg.norm(a, axis=1, keepdims=True)
    b = b / np.linalg.norm(b, axis=1, keepdims=True)
    return float((a * b).sum(axis=1).mean())


@dataclass
class MetricResult:
    """A metric value plus its matched-control calibration."""

    name: str
    value: float
    control: float | None = None
    delta: float | None = None
    ratio: float | None = None
    detail: dict | None = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value,
            "control": self.control,
            "delta": self.delta,
            "ratio": self.ratio,
            "detail": self.detail or {},
        }


def _calibrate(
    name: str, value: float, control: float | None, detail: dict | None = None
) -> MetricResult:
    delta = (value - control) if control is not None else None
    ratio = (value / control) if (control is not None and control != 0) else None
    return MetricResult(
        name=name, value=value, control=control, delta=delta, ratio=ratio, detail=detail
    )


def causal_trajectory_effect(
    future_a: np.ndarray,
    future_b: np.ndarray,
    control: tuple[np.ndarray, np.ndarray] | None = None,
) -> MetricResult:
    """CTE(X) = distance between the future distribution under do(X=a) and do(X=b).

    ``control`` is an optional matched pair ``(control_a, control_b)`` of
    non-intervened transitions; the CTE is reported relative to the control
    centroid distance so that generic drift is not read as an effect.
    """
    value = _centroid_distance(future_a, future_b)
    detail = {"mean_pairwise": _mean_pairwise_distance(future_a, future_b)}
    ctrl = _centroid_distance(control[0], control[1]) if control is not None else None
    return _calibrate("causal_trajectory_effect", value, ctrl, detail)


def branch_redirection_probability(
    future: np.ndarray,
    baseline: np.ndarray,
    control: np.ndarray | None = None,
    radius_quantile: float = 0.9,
) -> MetricResult:
    """BRP = P(future leaves the baseline semantic basin | do(intervention)).

    The basin is a :class:`~causal_mind.causal.basin.SemanticBasin` fit on
    ``baseline`` (the ball around the baseline centroid containing the central
    ``radius_quantile`` fraction of baseline points), so the radius is
    calibrated on the pre-intervention distribution only.
    """
    future = _as_2d(future)
    basin = SemanticBasin.fit(baseline, quantile=radius_quantile)
    fut_dists = basin.distances(future)
    brp = float(np.mean(fut_dists > basin.radius)) if len(fut_dists) else 0.0
    ctrl = None
    if control is not None:
        ctrl_dists = basin.distances(control)
        ctrl = float(np.mean(ctrl_dists > basin.radius)) if len(ctrl_dists) else 0.0
    return _calibrate("branch_redirection_probability", brp, ctrl, {"basin_radius": basin.radius})


def trajectory_persistence(
    future: np.ndarray, current: np.ndarray, control: np.ndarray | None = None
) -> MetricResult:
    """Mean cosine similarity between the future and the current state.

    High persistence = the future stays in the same semantic direction as the
    current state.
    """
    future, current = _as_2d(future), _as_2d(current)
    value = _mean_cosine(future, np.tile(current, (len(future), 1)))
    if control is not None:
        ctrl = _mean_cosine(control, np.tile(current, (len(control), 1)))
    else:
        ctrl = None
    return _calibrate("trajectory_persistence", value, ctrl)


def trajectory_divergence(
    future_a: np.ndarray,
    future_b: np.ndarray,
    control: tuple[np.ndarray, np.ndarray] | None = None,
) -> MetricResult:
    """Mean pairwise distance between two intervened branches (how far they drift)."""
    value = _mean_pairwise_distance(future_a, future_b)
    ctrl = _mean_pairwise_distance(control[0], control[1]) if control is not None else None
    return _calibrate("trajectory_divergence", value, ctrl)


def intervention_effect_decay(
    effects: np.ndarray, times: np.ndarray | None = None
) -> MetricResult:
    """Fit an exponential decay to a sequence of intervention effects over horizon.

    ``effects[k]`` is the effect size at horizon ``times[k]`` (defaults to 0..K-1).
    Returns the fitted half-life (in time units) and the decay rate. A flat or
    increasing effect yields a non-finite (no-decay) half-life.
    """
    effects = np.asarray(effects, dtype=float)
    if times is None:
        times = np.arange(len(effects), dtype=float)
    times = np.asarray(times, dtype=float)
    pos = effects > 0
    if pos.sum() < 2:
        return MetricResult(
            "intervention_effect_decay", float("nan"), detail={"n_positive": int(pos.sum())}
        )
    log_e = np.log(effects[pos])
    t = times[pos]
    # least-squares fit log(e) = a - b * t  =>  e = exp(a) * exp(-b t)
    A = np.column_stack([np.ones_like(t), t])
    coef, *_ = np.linalg.lstsq(A, log_e, rcond=None)
    b = float(-coef[1])
    half_life = float(np.log(2.0) / b) if b > 0 else float("inf")
    return MetricResult(
        "intervention_effect_decay",
        half_life,
        detail={"decay_rate": b, "initial_effect": float(np.exp(coef[0]))},
    )


def transitions_from_sequence(states: np.ndarray) -> np.ndarray:
    """Build ``(pre, post)`` transition pairs from a state sequence.

    ``states`` has shape ``(T, d)``; the result has shape ``(T - 1, 2d)``
    where row ``i`` is the concatenation of ``states[i]`` (pre) and
    ``states[i + 1]`` (post).
    """
    s = _as_2d(states)
    return np.concatenate([s[:-1], s[1:]], axis=1)


def sample_matched_controls(
    transitions: np.ndarray,
    query_pre: np.ndarray,
    n: int,
    seed: int | None = None,
) -> np.ndarray:
    """Draw matched control post-states for a query pre-state.

    ``transitions`` has shape ``(m, 2d)``: the first ``d`` columns are the
    pre-state and the last ``d`` the post-state of each observational
    (non-intervened) transition. Matching rule: control transitions are ranked
    by cosine distance between their pre-state and ``query_pre`` and the
    post-states of the ``n`` closest are returned.

    Limitations: matching is on the pre-state direction only (cosine, in the
    frozen embedding space) and does not guarantee an exact match; in sparse
    regions of the pre-state distribution the closest control pre-state may
    still be far from the query. If ``n > m`` all ``m`` post-states are
    returned (no replacement). Ties are broken by a seeded ``1e-12`` jitter on
    the distances, so a fixed ``seed`` makes the draw deterministic.
    """
    t = np.asarray(transitions, dtype=float)
    if t.ndim != 2 or t.shape[1] % 2 != 0:
        raise ValueError(f"transitions must have shape (m, 2d), got {t.shape}")
    d = t.shape[1] // 2
    pres, posts = t[:, :d], t[:, d:]
    q = np.asarray(query_pre, dtype=float).reshape(-1)
    if q.shape[0] != d:
        raise ValueError(f"query_pre has dimension {q.shape[0]}, expected {d}")
    pre_norms = np.linalg.norm(pres, axis=1, keepdims=True)
    pre_n = pres / np.where(pre_norms == 0.0, 1.0, pre_norms)
    q_norm = float(np.linalg.norm(q))
    qn = q if q_norm == 0.0 else q / q_norm
    dists = 1.0 - pre_n @ qn
    rng = np.random.default_rng(seed)
    dists = dists + rng.random(len(dists)) * 1e-12
    order = np.argsort(dists, kind="stable")
    k = min(n, len(order))
    return posts[order[:k]].copy()


def trajectory_effect_over_horizon(
    post_states: np.ndarray,
    control_states: np.ndarray,
    times: np.ndarray | None = None,
) -> MetricResult:
    """Per-horizon intervention effect vs a matched control, and its decay.

    ``post_states`` and ``control_states`` each have shape ``(H, d)``: the
    post-intervention state and the matched control state at each horizon
    ``h = 1..H`` (``times`` defaults to ``1..H``). The per-horizon effect is
    ``e[h] = ||post_states[h] - control_states[h]||``. The returned value is
    the fitted half-life of ``e`` (via :func:`intervention_effect_decay`): a
    large half-life means the effect persists beyond the immediate one-step.
    ``detail`` carries the per-horizon effect vector and the decay fit.
    """
    post = _as_2d(post_states)
    ctrl = _as_2d(control_states)
    if post.shape[0] != ctrl.shape[0]:
        raise ValueError(f"horizon mismatch: {post.shape[0]} vs {ctrl.shape[0]} states")
    if times is None:
        times = np.arange(1, post.shape[0] + 1, dtype=float)
    effects = np.linalg.norm(post - ctrl, axis=1)
    decay = intervention_effect_decay(effects, times)
    detail = {"per_horizon_effect": effects.tolist()}
    if decay.detail:
        detail.update(decay.detail)
    return MetricResult(
        name="trajectory_effect_over_horizon",
        value=decay.value,
        detail=detail,
    )
