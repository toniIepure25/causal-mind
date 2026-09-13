"""Tests for the CM-5 fusion model and destructive negative controls.

Synthetic data where the target = behavior signal + neural signal + noise. The
neural features genuinely predict the behavioral model's residual, so M4
(behavior+nuisance+neural) must beat M2 (behavior+nuisance). Each destructive
control must collapse that incremental neural gain.
"""
from __future__ import annotations

import numpy as np
import pytest

from causal_mind.neural.fusion import (FusionModel, incremental_neural_gain,
                                       score_cosine)
from causal_mind.neural.negative_controls import (ALL_CONTROLS, SubjectSample,
                                                  nc1_subject_permute,
                                                  nc2_temporal_shift,
                                                  nc4_nuisance_only,
                                                  nc5_neural_randomize,
                                                  nc6_target_permute)

N_SUBJ, N_PER, NB, NN, NC, DIM = 6, 60, 8, 10, 5, 32


def make_synthetic(seed: int = 0) -> list[SubjectSample]:
    rng = np.random.default_rng(seed)
    data = []
    for s in range(N_SUBJ):
        B = rng.normal(size=(N_PER, NB))
        N = rng.normal(size=(N_PER, NN))
        C = rng.normal(size=(N_PER, NC))
        Wb = rng.normal(size=(NB, DIM))
        Wn = rng.normal(size=(NN, DIM)) * 1.5  # strong neural signal
        target = B @ Wb + N @ Wn + 0.4 * rng.normal(size=(N_PER, DIM))
        data.append(SubjectSample(f"sub-{s}", B, N, C, target))
    return data


def _stack(data, attr):
    return np.concatenate([getattr(d, attr) for d in data], axis=0)


def _fit_score(data, use_neural, use_nuisance):
    m = FusionModel(alpha=10.0, use_neural=use_neural, use_nuisance=use_nuisance)
    m.fit(_stack(data, "behavior"), _stack(data, "target"),
          _stack(data, "neural"), _stack(data, "nuisance"))
    pred = m.predict(_stack(data, "behavior"), _stack(data, "neural"),
                     _stack(data, "nuisance"))
    return score_cosine(pred, _stack(data, "target"))


def test_incremental_neural_gain_positive():
    data = make_synthetic()
    s_m2 = _fit_score(data, use_neural=False, use_nuisance=True)
    s_m4 = _fit_score(data, use_neural=True, use_nuisance=True)
    gain = incremental_neural_gain(s_m4, s_m2)
    assert s_m4 > s_m2
    assert gain > 0.02  # a clear incremental neural gain


def test_controls_collapse_neural_gain():
    data = make_synthetic()
    rng = np.random.default_rng(1)
    s_m2 = _fit_score(data, use_neural=False, use_nuisance=True)
    base_gain = incremental_neural_gain(_fit_score(data, True, True), s_m2)
    assert base_gain > 0.02

    def gain_after(ctl_data):
        return incremental_neural_gain(_fit_score(ctl_data, True, True), s_m2)

    # controls that destroy the neural signal must collapse the gain
    assert gain_after(nc1_subject_permute(data, rng)) < base_gain / 2
    assert gain_after(nc2_temporal_shift(data, shift=7, rng=rng)) < base_gain / 2
    assert gain_after(nc5_neural_randomize(data, rng)) < base_gain / 2
    assert gain_after(nc6_target_permute(data, rng)) < base_gain / 2
    # NC4 (nuisance only) zeroes the neural features -> no neural gain
    assert gain_after(nc4_nuisance_only(data)) < base_gain / 2


def test_all_controls_registered():
    assert set(ALL_CONTROLS) == {"NC1_subject_perm", "NC2_temporal_shift",
                                 "NC3_block_perm", "NC4_nuisance_only",
                                 "NC5_neural_randomize", "NC6_target_perm"}


def test_nc3_block_permute_preserves_shape():
    data = make_synthetic()
    rng = np.random.default_rng(2)
    from causal_mind.neural.negative_controls import nc3_block_permute
    out = nc3_block_permute(data, block=5, rng=rng)
    for d, o in zip(data, out, strict=True):
        assert o.neural.shape == d.neural.shape
        assert o.subject == d.subject
