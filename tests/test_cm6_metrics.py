from __future__ import annotations

import numpy as np
import pytest

from causal_mind.causal import (
    branch_redirection_probability,
    causal_trajectory_effect,
    intervention_effect_decay,
    trajectory_divergence,
    trajectory_persistence,
)


def test_cte_large_shift_gives_large_effect() -> None:
    rng = np.random.default_rng(0)
    base = rng.normal(size=(60, 16))
    fut_a = base + 0.05
    fut_b = base + 5.0
    res = causal_trajectory_effect(fut_a, fut_b)
    assert res.value > 4.0
    assert res.name == "causal_trajectory_effect"


def test_cte_with_control_calibration() -> None:
    rng = np.random.default_rng(1)
    base = rng.normal(size=(60, 16))
    fut_a, fut_b = base + 0.05, base + 5.0
    ctrl_a, ctrl_b = base + 0.05, base + 0.1  # tiny control drift
    res = causal_trajectory_effect(fut_a, fut_b, control=(ctrl_a, ctrl_b))
    assert res.control is not None
    assert res.delta is not None and res.delta > 0
    assert res.value > res.control


def test_cte_no_shift_small() -> None:
    rng = np.random.default_rng(2)
    base = rng.normal(size=(200, 16))
    res = causal_trajectory_effect(base, base + rng.normal(scale=0.01, size=(200, 16)))
    assert res.value < 0.5


def test_brp_far_shift_high_near_shift_low() -> None:
    rng = np.random.default_rng(3)
    baseline = rng.normal(size=(200, 16))
    c = baseline.mean(axis=0)
    far = c[None, :] + 30.0  # far from the baseline centroid
    near = c[None, :] + rng.normal(scale=0.01, size=(50, 16))  # tight around centroid
    assert branch_redirection_probability(far, baseline).value > 0.9
    assert branch_redirection_probability(near, baseline).value < 0.1


def test_brp_with_control() -> None:
    rng = np.random.default_rng(4)
    baseline = rng.normal(size=(200, 16))
    fut = baseline + 6.0
    ctrl = baseline + 0.1
    res = branch_redirection_probability(fut, baseline, control=ctrl)
    assert res.value > res.control


def test_trajectory_persistence_high_when_staying() -> None:
    rng = np.random.default_rng(5)
    current = rng.normal(size=16)
    future = current[None, :] + rng.normal(scale=0.05, size=(50, 16))
    res = trajectory_persistence(future, current)
    assert res.value > 0.9
    future_far = current[None, :] + rng.normal(scale=5.0, size=(50, 16))
    assert trajectory_persistence(future_far, current).value < res.value


def test_trajectory_divergence_grows_with_separation() -> None:
    rng = np.random.default_rng(6)
    base = rng.normal(size=(50, 16))
    close = trajectory_divergence(base, base + 0.1)
    far = trajectory_divergence(base, base + 6.0)
    assert far.value > close.value


def test_intervention_effect_decay_half_life() -> None:
    # effects = 1.0 * 2^(-t)  => half-life of 1.0 time unit
    t = np.arange(0.0, 8.0)
    effects = np.power(2.0, -t)
    res = intervention_effect_decay(effects, t)
    assert res.value == pytest.approx(1.0, rel=0.05)
    assert res.detail["decay_rate"] == pytest.approx(np.log(2.0), rel=0.05)


def test_intervention_effect_decay_no_decay() -> None:
    effects = np.ones(5)  # flat -> no decay -> inf half-life
    res = intervention_effect_decay(effects)
    assert np.isinf(res.value)


def test_metric_result_as_dict() -> None:
    res = causal_trajectory_effect(np.zeros((5, 4)), np.ones((5, 4)))
    d = res.as_dict()
    assert d["name"] == "causal_trajectory_effect"
    assert "value" in d and "control" in d
