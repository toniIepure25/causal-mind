"""Compact candidate forecasting models (CM-2E).

Progression (simple first, capacity matched to data size, NO giant trainable LLM):
1. ``LinearTransition`` -- ridge regression mapping a fixed window of history
   embeddings to the next embedding (the primary "learned transition" model).
2. ``GRUNext`` -- a small 1-2 layer GRU over history embeddings (torch, CPU),
   used only if the linear model leaves demonstrable headroom.

All models are trained on TRAIN subjects only and evaluated on the sealed
test subjects. The text encoder is frozen; embeddings are precomputed/cached.
"""
from __future__ import annotations

import numpy as np

from causal_mind.thought.prospective import Sample
from causal_mind.thought.state_v1 import ThoughtState


def _hist_feat(sample: Sample, states: list[ThoughtState]) -> np.ndarray:
    """Flatten the last-k history embeddings into one row (oldest -> newest)."""
    rows = [states[i].embedding for i in sample.history]
    return np.concatenate(rows)


def build_xy(
    samples: list[Sample],
    states_by_subject: dict[str, list[ThoughtState]],
) -> tuple[np.ndarray, np.ndarray]:
    """Feature/target matrices for training (history -> next embedding)."""
    Xs, Ys = [], []
    for s in samples:
        st = states_by_subject[s.subject]
        Xs.append(_hist_feat(s, st))
        Ys.append(st[s.target_index].embedding)
    return np.vstack(Xs), np.vstack(Ys)


class LinearTransition:
    """Ridge regression: history window (k x dim) -> next embedding (dim)."""

    name = "linear_transition"

    def __init__(self, k: int = 1, alpha: float = 10.0) -> None:
        self.k = k
        self.alpha = alpha
        self._ridge = None

    def fit(self, X: np.ndarray, Y: np.ndarray) -> LinearTransition:
        from sklearn.linear_model import Ridge

        self._ridge = Ridge(alpha=self.alpha)
        self._ridge.fit(X, Y)
        return self

    def predict(self, sample: Sample, states: list[ThoughtState]) -> np.ndarray:
        x = _hist_feat(sample, states)
        return self._ridge.predict(x.reshape(1, -1))[0]

    def param_count(self) -> int:
        if self._ridge is None:
            return 0
        return int(self._ridge.coef_.size + self._ridge.intercept_.size)


class GRUNext:
    """Small GRU over a window of history embeddings -> next embedding (torch, CPU)."""

    name = "gru_next"

    def __init__(self, k: int = 1, dim: int = 384, hidden: int = 64, layers: int = 1,
                 epochs: int = 30, lr: float = 3e-3, batch: int = 256, seed: int = 0) -> None:
        self.k, self.dim, self.hidden, self.layers = k, dim, hidden, layers
        self.epochs, self.lr, self.batch, self.seed = epochs, lr, batch, seed
        self._model = None

    def _build(self, X: np.ndarray, Y: np.ndarray):
        import torch
        import torch.nn as nn

        torch.manual_seed(self.seed)

        dim, hidden, layers = self.dim, self.hidden, self.layers

        class _GRUNet(nn.Module):
            def __init__(self) -> None:
                super().__init__()
                self.gru = nn.GRU(dim, hidden, num_layers=layers, batch_first=True)
                self.fc = nn.Linear(hidden, dim)

            def forward(self, x):  # noqa: D102
                out, _ = self.gru(x)
                return self.fc(out[:, -1, :])

        net = _GRUNet()
        self._model = net
        self._opt = torch.optim.Adam(net.parameters(), lr=self.lr)
        self._X = torch.tensor(X, dtype=torch.float32).reshape(-1, self.k, self.dim)
        self._Y = torch.tensor(Y, dtype=torch.float32)

    def fit(self, X: np.ndarray, Y: np.ndarray) -> GRUNext:
        self._build(X, Y)
        import torch

        n = self._X.shape[0]
        for _ in range(self.epochs):
            perm = torch.randperm(n)
            for i in range(0, n, self.batch):
                idx = perm[i:i + self.batch]
                pred = self._model(self._X[idx])
                loss = torch.nn.functional.mse_loss(pred, self._Y[idx])
                self._opt.zero_grad()
                loss.backward()
                self._opt.step()
        self._model.eval()
        return self

    def predict(self, sample: Sample, states: list[ThoughtState]) -> np.ndarray:
        import torch

        rows = torch.tensor(
            np.stack([states[i].embedding for i in sample.history]), dtype=torch.float32
        ).reshape(1, self.k, self.dim)
        with torch.no_grad():
            out = self._model(rows)
        return out[0].numpy()

    def param_count(self) -> int:
        if self._model is None:
            return 0
        return int(sum(p.numel() for p in self._model.parameters()))
