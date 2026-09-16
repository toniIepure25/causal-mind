from __future__ import annotations

import numpy as np
import pytest

from causal_mind.causal.basin import SemanticBasin
from causal_mind.causal.metrics import (
    branch_redirection_probability,
    causal_trajectory_effect,
    intervention_effect_decay,
    sample_matched_controls,
    trajectory_divergence,
    trajectory_effect_over_horizon,
    transitions_from_sequence,
)


def test_basin_fits_baseline_and_rejects_shifted_cluster() -> None:
    rng = np.random.default_rng(0)
    baseline = rng.normal(size=(300, 16))
    basin = SemanticBasin.fit(baseline, quantile=0.9)
    assert basin.n_reference == 300
    assert basin.radius > 0.0
    assert basin.probability_inside(baseline) > 0.85
    shifted = baseline.mean(axis=0)[None, :] + 20.0
    assert basin.probability_inside(shifted) < 0.05
    assert basin.contains(baseline).shape == (300,)
    assert not basin.contains(shifted).any()


def test_basin_quantile_controls_radius() -> None:
    rng = np.random.default_rng(1)
    baseline = rng.normal(size=(400, 8))
    tight = SemanticBasin.fit(baseline, quantile=0.5)
    loose = SemanticBasin.fit(baseline, quantile=0.95)
    assert tight.radius < loose.radius
    assert tight.probability_inside(baseline) < loose.probability_inside(baseline)


def test_brp_uses_basin_and_keeps_backward_compatible_detail() -> None:
    rng = np.random.default_rng(2)
    baseline = rng.normal(size=(200, 16))
    basin = SemanticBasin.fit(baseline, quantile=0.9)
    far = baseline.mean(axis=0)[None, :] + 30.0
    res = branch_redirection_probability(far, baseline)
    assert res.value > 0.9
    assert res.detail["basin_radius"] == pytest.approx(basin.radius)


def test_transitions_from_sequence() -> None:
    states = np.arange(12, dtype=float).reshape(4, 3)
    trans = transitions_from_sequence(states)
    assert trans.shape == (3, 6)
    assert np.allclose(trans[0], [0, 1, 2, 3, 4, 5])


def test_sample_matched_controls_selects_closest_pre_states() -> None:
    rng = np.random.default_rng(3)
    pres = rng.normal(size=(50, 8))
    posts = pres + 0.1
    transitions = np.concatenate([pres, posts], axis=1)
    query = pres[7]
    out = sample_matched_controls(transitions, query, n=5, seed=0)
    assert out.shape == (5, 8)
    assert np.allclose(out[0], posts[7])
    assert np.allclose(sample_matched_controls(transitions, query, n=5, seed=0), out)
    assert sample_matched_controls(transitions, query, n=999, seed=0).shape == (50, 8)
    with pytest.raises(ValueError):
        sample_matched_controls(transitions, np.zeros(4), n=1)


def _toy_scm_one_step(rng: np.random.Generator, n: int, d: int, shift: np.ndarray):
    """One step of a toy SCM: Z[t+1] = Z[t] + do(Z) + eps.

    The intervention arm applies do(Z) = +shift to the pre-state; the control
    arm does not. Both arms share the same pre-state cloud, so the control
    post-states are the matched counterfactual of the intervention pre-states.
    """
    baseline = rng.normal(size=(n, d))
    post_int = baseline + shift + rng.normal(scale=0.05, size=(n, d))
    post_ctrl = baseline + rng.normal(scale=0.05, size=(n, d))
    return baseline, post_int, post_ctrl


def test_e2e_intervention_larger_than_matched_control() -> None:
    rng = np.random.default_rng(4)
    d, n = 16, 200
    shift = 6.0 * np.ones(d)
    baseline, post_int, post_ctrl = _toy_scm_one_step(rng, n, d, shift)

    trans = np.concatenate([baseline, post_ctrl], axis=1)
    ctrl_matched = np.stack(
        [sample_matched_controls(trans, baseline[i], n=1, seed=0)[0] for i in range(n)]
    )
    assert np.allclose(ctrl_matched, post_ctrl, atol=1e-6)

    ctrl_a, ctrl_b = post_ctrl[: n // 2], post_ctrl[n // 2 :]

    cte = causal_trajectory_effect(post_int, ctrl_matched, control=(ctrl_a, ctrl_b))
    assert cte.value > 4.0
    assert cte.delta is not None and cte.delta > 0

    brp = branch_redirection_probability(post_int, baseline, control=ctrl_matched)
    assert brp.value > 0.9
    assert brp.delta is not None and brp.delta > 0

    div = trajectory_divergence(post_int, ctrl_matched, control=(ctrl_a, ctrl_b))
    assert div.value > 4.0
    assert div.delta is not None and div.delta > 0

    # intervention == control: the effect vs the matched control collapses to
    # ~0 and the calibrated delta is bounded by the control's own drift
    cte0 = causal_trajectory_effect(post_ctrl, ctrl_matched, control=(ctrl_a, ctrl_b))
    assert cte0.value < 0.5
    assert abs(cte0.delta or 0.0) < cte0.control + 1.0
    brp0 = branch_redirection_probability(post_ctrl, baseline, control=ctrl_matched)
    assert brp0.value < 0.2
    div0 = trajectory_divergence(post_ctrl, ctrl_matched, control=(ctrl_a, ctrl_b))
    assert div0.delta is not None and abs(div0.delta) < 0.5


def _run_toy_scm_horizon(
    rng: np.random.Generator, z0: np.ndarray, shock: np.ndarray, phi: float, H: int
) -> np.ndarray:
    """Toy linear SCM Z[t+1] = phi * Z[t] + eps with a one-time shock at t=0."""
    z = z0 + shock
    rows = [z.copy()]
    for _ in range(H):
        z = phi * z + rng.normal(scale=0.01, size=z0.shape)
        rows.append(z.copy())
    return np.stack(rows)


def test_e2e_horizon_effect_recovers_known_half_life() -> None:
    rng = np.random.default_rng(5)
    d, phi, H = 16, 0.9, 12
    z0 = rng.normal(size=d)
    shift = 5.0 * np.ones(d) / np.sqrt(d)  # unit-norm direction, magnitude 5

    post = _run_toy_scm_horizon(rng, z0, shift, phi, H)
    ctrl = _run_toy_scm_horizon(rng, z0, np.zeros(d), phi, H)
    res = trajectory_effect_over_horizon(post, ctrl)
    expected_hl = np.log(2.0) / np.log(1.0 / phi)
    assert res.value == pytest.approx(expected_hl, rel=0.15)
    effects = res.detail["per_horizon_effect"]
    assert effects[0] == pytest.approx(5.0, rel=0.1)
    assert effects[-1] < effects[0]

    no_shift = trajectory_effect_over_horizon(
        _run_toy_scm_horizon(rng, z0, np.zeros(d), phi, H),
        _run_toy_scm_horizon(rng, z0, np.zeros(d), phi, H),
    )
    assert max(no_shift.detail["per_horizon_effect"]) < 0.2


def test_horizon_metric_rejects_mismatched_horizons() -> None:
    with pytest.raises(ValueError):
        trajectory_effect_over_horizon(np.zeros((3, 4)), np.zeros((4, 4)))


def test_decay_recovers_non_unit_half_life() -> None:
    t = np.arange(0.0, 20.0)
    effects = np.power(2.0, -t / 3.0)
    res = intervention_effect_decay(effects, t)
    assert res.value == pytest.approx(3.0, rel=0.05)
    assert res.detail["decay_rate"] == pytest.approx(np.log(2.0) / 3.0, rel=0.05)
