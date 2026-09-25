"""Low-level numeric utilities (no internal dependencies).

Kept dependency-free so both ``eval`` and ``forecast`` can share it without a
circular import (CM-REPO S3).
"""
from __future__ import annotations

import numpy as np


def cosines(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Cosine of vector ``a`` against each row of matrix ``B`` (B: (N, dim))."""
    B = np.atleast_2d(B)
    na = np.linalg.norm(a)
    if na == 0:
        return np.zeros(B.shape[0], dtype=float)
    nb = np.linalg.norm(B, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sims = B @ a / (nb * na)
    return np.where(nb > 0, sims, 0.0)
