"""Destructive negative controls NC1-NC6 (CM-5).

A real neural gain must collapse under the relevant destructive controls. Each
control breaks a specific aspect of the neural-behavioral correspondence while
preserving as much marginal structure as possible, so a surviving "gain" would
indicate a shortcut rather than genuine prospective neural information.

All controls are pure data manipulations on per-subject feature arrays and are
unit-tested on synthetic data (a neural signal that genuinely predicts the
future must disappear after the relevant control).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SubjectSample:
    subject: str
    behavior: np.ndarray   # (n, nb) behavioral features
    neural: np.ndarray     # (n, nn) neural features
    nuisance: np.ndarray   # (n, nc) nuisance features
    target: np.ndarray     # (n, dim) true future embedding


def nc1_subject_permute(data: list[SubjectSample], rng: np.random.Generator) -> list[SubjectSample]:
    """NC1: pair each subject's behavior with a WRONG subject's neural data."""
    out = []
    for i, d in enumerate(data):
        j = rng.integers(0, len(data))
        while j == i and len(data) > 1:
            j = rng.integers(0, len(data))
        other = data[int(j)]
        n = min(d.neural.shape[0], other.neural.shape[0])
        out.append(SubjectSample(d.subject, d.behavior[:n], other.neural[:n],
                                 d.nuisance[:n], d.target[:n]))
    return out


def nc2_temporal_shift(data: list[SubjectSample], shift: int,
                       rng: np.random.Generator) -> list[SubjectSample]:
    """NC2: shift each subject's neural time series (destroys temporal coupling,
    preserves autocorrelation structure)."""
    out = []
    for d in data:
        s = shift if shift != 0 else int(rng.integers(1, max(2, d.neural.shape[0] // 2)))
        neural = np.roll(d.neural, shift=s, axis=0)
        out.append(SubjectSample(d.subject, d.behavior, neural, d.nuisance, d.target))
    return out


def nc3_block_permute(data: list[SubjectSample], block: int,
                      rng: np.random.Generator) -> list[SubjectSample]:
    """NC3: within-subject block permutation (preserves coarse temporal
    properties, breaks the thought-neural correspondence)."""
    out = []
    for d in data:
        n = d.neural.shape[0]
        nb = max(1, n // block)
        order = rng.permutation(nb)
        neural = np.empty_like(d.neural)
        for new_i, old_i in enumerate(order):
            a, b = new_i * block, (new_i + 1) * block
            neural[a:b] = d.neural[old_i * block: old_i * block + block]
        neural[nb * block:] = d.neural[nb * block:]  # keep the tail
        out.append(SubjectSample(d.subject, d.behavior, neural, d.nuisance, d.target))
    return out


def nc4_nuisance_only(data: list[SubjectSample]) -> list[SubjectSample]:
    """NC4: zero out the neural features (motion/speech metadata only)."""
    out = []
    for d in data:
        neural = np.zeros_like(d.neural)
        out.append(SubjectSample(d.subject, d.behavior, neural, d.nuisance, d.target))
    return out


def nc5_neural_randomize(data: list[SubjectSample],
                         rng: np.random.Generator) -> list[SubjectSample]:
    """NC5: destroy neural spatial structure (independently permute each
    feature's values across samples)."""
    out = []
    for d in data:
        neural = np.empty_like(d.neural)
        for j in range(d.neural.shape[1]):
            neural[:, j] = d.neural[rng.permutation(d.neural.shape[0]), j]
        out.append(SubjectSample(d.subject, d.behavior, neural, d.nuisance, d.target))
    return out


def nc6_target_permute(data: list[SubjectSample],
                       rng: np.random.Generator) -> list[SubjectSample]:
    """NC6: permute the target rows within each subject (frozen valid
    permutation; breaks the neural->future correspondence)."""
    out = []
    for d in data:
        target = d.target[rng.permutation(d.target.shape[0])]
        out.append(SubjectSample(d.subject, d.behavior, d.neural, d.nuisance, target))
    return out


ALL_CONTROLS = {
    "NC1_subject_perm": nc1_subject_permute,
    "NC2_temporal_shift": nc2_temporal_shift,
    "NC3_block_perm": nc3_block_permute,
    "NC4_nuisance_only": nc4_nuisance_only,
    "NC5_neural_randomize": nc5_neural_randomize,
    "NC6_target_perm": nc6_target_permute,
}
