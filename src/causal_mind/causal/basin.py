"""Semantic basin: calibrated "normal range" region in embedding space.

A :class:`SemanticBasin` formalizes the region of the frozen semantic
embedding space occupied by the *baseline* (pre-intervention / non-intervened)
distribution. It is the calibration object that turns raw embedding movement
into a meaningful signal: movement is only interpretable relative to the
basin, and the basin must be fit on baseline data alone so it cannot be
contaminated by the intervention under study.

Design choice: a ball around the reference centroid whose radius is set at a
given quantile of the reference distances (rather than a k-NN /
local-density radius). Reasons:

* per-subject thought baselines in this project are approximately
  single-cluster clouds in the frozen MiniLM space, so a global ball is a
  faithful model of "where the baseline is";
* the quantile ball has one interpretable hyperparameter (the quantile) and
  is stable for small reference samples, while a k-NN radius depends on a
  neighbor count ``k`` whose effect interacts with sample size and ambient
  dimensionality;
* it exactly reproduces the v0 BRP radius, so historical metric values stay
  comparable.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _as_2d(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    return x


@dataclass
class SemanticBasin:
    """Ball around the baseline centroid covering ``quantile`` of the reference.

    Attributes
    ----------
    centroid:
        Centroid of the reference (baseline) embeddings, shape ``(d,)``.
    radius:
        Distance from the centroid containing the central ``quantile``
        fraction of the reference points.
    quantile:
        Quantile of the reference distance distribution used for ``radius``.
    n_reference:
        Number of reference embeddings the basin was fit on.
    """

    centroid: np.ndarray
    radius: float
    quantile: float = 0.9
    n_reference: int = 0

    @classmethod
    def fit(cls, reference: np.ndarray, quantile: float = 0.9) -> SemanticBasin:
        """Fit a basin to ``reference`` embeddings (baseline distribution only)."""
        ref = _as_2d(reference)
        centroid = ref.mean(axis=0)
        dists = np.linalg.norm(ref - centroid, axis=1)
        radius = float(np.quantile(dists, quantile)) if len(dists) else 0.0
        return cls(
            centroid=centroid,
            radius=radius,
            quantile=float(quantile),
            n_reference=len(ref),
        )

    def distances(self, x: np.ndarray) -> np.ndarray:
        """Euclidean distance from each embedding in ``x`` to the centroid."""
        return np.linalg.norm(_as_2d(x) - self.centroid, axis=1)

    def contains(self, x: np.ndarray) -> np.ndarray:
        """Boolean mask: which embeddings of ``x`` lie inside the basin."""
        return self.distances(x) <= self.radius

    def probability_inside(self, x: np.ndarray) -> float:
        """Fraction of the embeddings in ``x`` that lie inside the basin."""
        inside = self.contains(x)
        return float(inside.mean()) if len(inside) else 0.0

    def to_dict(self) -> dict:
        return {
            "centroid": self.centroid,
            "radius": self.radius,
            "quantile": self.quantile,
            "n_reference": self.n_reference,
        }
