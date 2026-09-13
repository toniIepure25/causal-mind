"""Behavioral + neural fusion models M0-M4 and the residual-correction test (CM-5).

The decisive contrast is IncrementalNeuralGain = score(M4) - score(M2), where
    M2 = behavior + nuisance
    M4 = behavior + nuisance + neural
Both are built as a frozen behavioral prediction plus a residual correction so
the scientific hypothesis is clean:

    future_hat = behavior_hat + residual_hat
    residual   = true_future - behavior_hat

The residual is predicted from (neural + nuisance) features. If neural activity
predicts the behavioral model's held-out residuals, the brain carries
information absent from observable thought history.

All models are linear (ridge) and TRAIN-fitted; nothing is fit on val/test.
Works on plain feature matrices so it is unit-tested on synthetic data.
"""
from __future__ import annotations

import numpy as np
from sklearn.linear_model import Ridge

from causal_mind.eval.protocol import cosine


def _fit_ridge(X: np.ndarray, Y: np.ndarray, alpha: float) -> Ridge:
    return Ridge(alpha=alpha).fit(X, Y)


class FusionModel:
    """future_hat = behavior_hat + residual_hat.

    ``behavior`` features always enter (the frozen behavioral predictor).
    ``neural`` and/or ``nuisance`` features enter only through the residual
    correction. Configurations:
      M0: use_neural=False, use_nuisance=False  (behavior only)
      M2: use_neural=False, use_nuisance=True   (behavior + nuisance)
      M3: use_neural=True,  use_nuisance=False  (behavior + neural)
      M4: use_neural=True,  use_nuisance=True   (behavior + nuisance + neural)
    """

    def __init__(self, alpha: float = 100.0, use_neural: bool = True,
                 use_nuisance: bool = True) -> None:
        self.alpha = alpha
        self.use_neural = use_neural
        self.use_nuisance = use_nuisance
        self._behavior: Ridge | None = None
        self._residual: Ridge | None = None
        self._resid_dim = 0

    def _resid_features(self, X_neural: np.ndarray | None,
                        X_nuisance: np.ndarray | None) -> np.ndarray | None:
        parts = []
        if self.use_neural and X_neural is not None:
            parts.append(X_neural)
        if self.use_nuisance and X_nuisance is not None:
            parts.append(X_nuisance)
        if not parts:
            return None
        return np.concatenate(parts, axis=1)

    def fit(self, X_behavior: np.ndarray, Y: np.ndarray,
            X_neural: np.ndarray | None = None,
            X_nuisance: np.ndarray | None = None) -> FusionModel:
        self._behavior = _fit_ridge(X_behavior, Y, self.alpha)
        beh_hat = self._behavior.predict(X_behavior)
        residual = Y - beh_hat
        R = self._resid_features(X_neural, X_nuisance)
        if R is not None and R.shape[1] > 0:
            self._residual = _fit_ridge(R, residual, self.alpha)
            self._resid_dim = R.shape[1]
        return self

    def behavior_predict(self, X_behavior: np.ndarray) -> np.ndarray:
        return self._behavior.predict(X_behavior)

    def predict(self, X_behavior: np.ndarray,
                X_neural: np.ndarray | None = None,
                X_nuisance: np.ndarray | None = None) -> np.ndarray:
        out = self.behavior_predict(X_behavior)
        R = self._resid_features(X_neural, X_nuisance)
        if self._residual is not None and R is not None:
            out = out + self._residual.predict(R)
        return out


def neural_only(X_neural: np.ndarray, Y: np.ndarray,
                alpha: float = 100.0) -> np.ndarray:
    """M1: brain history -> future (scientific interest only)."""
    return _fit_ridge(X_neural, Y, alpha).predict(X_neural)


def score_cosine(pred: np.ndarray, true: np.ndarray) -> float:
    """Mean cosine between predicted and true future embeddings."""
    return float(np.mean([cosine(p, t) for p, t in zip(pred, true, strict=True)]))


def incremental_neural_gain(score_m4: float, score_m2: float) -> float:
    """The primary CM-5 quantity: M4 (behavior+nuisance+neural) - M2
    (behavior+nuisance)."""
    return score_m4 - score_m2
