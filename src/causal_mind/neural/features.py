"""Low-capacity neural feature ladder N1-N3 (CM-5).

Progression from coarse, interpretable to richer representations. All
spatial/transform operations that depend on the data are fitted on TRAIN only
(N3). Works on a 4-D BOLD volume array (n_volumes, nx, ny, nz) so it is
unit-tested on synthetic data and used on real fMRIPrep MNI BOLD once acquired.

N1 — global/network-level BOLD: mean time series of canonical networks.
N2 — atlas parcellation: parcel-wise mean time series.
N3 — train-fitted dimensionality reduction (PCA) on the N1/N2 features.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class NetworkDefinition:
    """A set of named masks (boolean arrays over the volume grid)."""
    names: list[str] = field(default_factory=list)
    masks: list[np.ndarray] = field(default_factory=list)


def network_mean_ts(bold_4d: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Mean BOLD time series within a mask: (n_volumes,)."""
    if bold_4d.shape[1:] != mask.shape:
        raise ValueError("mask shape must match the BOLD spatial shape")
    sel = bold_4d[:, mask]
    if sel.shape[1] == 0:
        raise ValueError("mask is empty")
    return sel.mean(axis=1)


def n1_network_features(bold_4d: np.ndarray, net: NetworkDefinition) -> np.ndarray:
    """N1: (n_volumes, n_networks) — one mean time series per network."""
    ts = [network_mean_ts(bold_4d, m) for m in net.masks]
    return np.stack(ts, axis=1)


def n2_atlas_features(bold_4d: np.ndarray, parcels: list[np.ndarray]) -> np.ndarray:
    """N2: (n_parcels, n_volumes) — parcel-wise mean time series."""
    ts = [network_mean_ts(bold_4d, p) for p in parcels]
    return np.stack(ts, axis=0)


class TrainPCA:
    """N3: PCA fitted on TRAIN only; applied to any subject's features."""

    def __init__(self, n_components: int = 20) -> None:
        self.n_components = n_components
        self._mean: np.ndarray | None = None
        self._components: np.ndarray | None = None
        self._fitted = False

    def fit(self, X_train: np.ndarray) -> TrainPCA:
        # X_train: (n_train_samples, n_features)
        self._mean = X_train.mean(axis=0)
        Xc = X_train - self._mean
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
        k = min(self.n_components, Vt.shape[0])
        self._components = Vt[:k]  # (k, n_features)
        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("TrainPCA must be fit on TRAIN before transform")
        return (X - self._mean) @ self._components.T


def window_feature(ts: np.ndarray, vol_indices: list[int]) -> np.ndarray:
    """Mean of a time series over the (HRF-safe) volume window."""
    if not vol_indices:
        raise ValueError("empty volume window")
    return ts[vol_indices].mean(axis=0)
