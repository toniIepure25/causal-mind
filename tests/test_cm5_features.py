"""Tests for the CM-5 neural feature ladder N1-N3 (synthetic BOLD)."""
from __future__ import annotations

import numpy as np

from causal_mind.neural.features import (
    NetworkDefinition,
    TrainPCA,
    n1_network_features,
    n2_atlas_features,
    network_mean_ts,
    window_feature,
)

NVOL, NX, NY, NZ = 100, 8, 8, 8


def _synthetic_bold(seed: int = 0):
    rng = np.random.default_rng(seed)
    bold = rng.normal(size=(NVOL, NX, NY, NZ)) * 0.1
    # a known signal (sine) in the left half of the volume
    left = np.zeros((NX, NY, NZ), dtype=bool)
    left[: NX // 2] = True
    signal = np.sin(np.linspace(0, 4 * np.pi, NVOL))
    n_left = int(left.sum())
    bold[:, left] = signal[:, None] + rng.normal(size=(NVOL, n_left)) * 0.05
    return bold, left, signal


def test_network_mean_ts_recovers_signal():
    bold, left, signal = _synthetic_bold()
    ts = network_mean_ts(bold, left)
    assert ts.shape == (NVOL,)
    # the recovered mean should correlate strongly with the true signal
    r = np.corrcoef(ts, signal)[0, 1]
    assert r > 0.95


def test_n1_network_features_shape():
    bold, left, _ = _synthetic_bold()
    right = ~left
    net = NetworkDefinition(names=["L", "R"], masks=[left, right])
    feats = n1_network_features(bold, net)
    assert feats.shape == (NVOL, 2)


def test_n2_atlas_features_shape():
    bold, left, _ = _synthetic_bold()
    quarter = np.zeros((NX, NY, NZ), dtype=bool)
    quarter[: NX // 2, : NY // 2] = True
    parcels = [left, ~left, quarter]
    feats = n2_atlas_features(bold, parcels)
    assert feats.shape == (3, NVOL)


def test_train_pca_fit_transform():
    rng = np.random.default_rng(1)
    X_train = rng.normal(size=(200, 30))
    X_test = rng.normal(size=(50, 30))
    pca = TrainPCA(n_components=10).fit(X_train)
    Z = pca.transform(X_test)
    assert Z.shape == (50, 10)
    # fitting on train then transforming test must not raise
    assert np.all(np.isfinite(Z))


def test_train_pca_requires_fit():
    pca = TrainPCA(n_components=5)
    try:
        pca.transform(np.zeros((10, 8)))
        raise AssertionError("expected RuntimeError before fit")
    except RuntimeError:
        pass


def test_window_feature_mean():
    ts = np.arange(20, dtype=float)
    assert window_feature(ts, [0, 1, 2]) == 1.0
    assert window_feature(ts, [10]) == 10.0
    try:
        window_feature(ts, [])
        raise AssertionError("expected ValueError on empty window")
    except ValueError:
        pass


def test_mask_shape_mismatch_raises():
    bold, _, _ = _synthetic_bold()
    bad = np.zeros((NX, NY, NZ - 1), dtype=bool)
    try:
        network_mean_ts(bold, bad)
        raise AssertionError("expected ValueError on shape mismatch")
    except ValueError:
        pass
