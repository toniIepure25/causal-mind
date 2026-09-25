"""Frozen CM-2 evaluation protocol (CM-2C).

Defined and SEALED before any comparative result is inspected:
* subject-disjoint train/val/test split (deterministic, seeded, sorted);
* a seal hash persisted to disk so the split cannot be quietly changed;
* primary metrics per target (semantic + categorical + timing);
* subject-level bootstrap CIs;
* a permutation null that destroys the temporal correspondence.

NO random thought-level row split anywhere.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from causal_mind import paths
from causal_mind.utils.metrics import cosines  # noqa: F401  (re-export for back-compat)

SEAL_PATH = paths.cm2_split_seal()


@dataclass(frozen=True)
class Split:
    train: tuple[str, ...]
    val: tuple[str, ...]
    test: tuple[str, ...]

    def subjects_of(self, part: str) -> tuple[str, ...]:
        return {"train": self.train, "val": self.val, "test": self.test}[part]

    def to_dict(self) -> dict:
        return {"train": list(self.train), "val": list(self.val), "test": list(self.test)}


def subject_disjoint_split(subjects: list[str], seed: int = 20260911,
                           train_frac: float = 0.70, val_frac: float = 0.15) -> Split:
    """Deterministic subject-disjoint split. Subjects are shuffled by a seeded
    RNG and cut into train/val/test. No thought-level rows are split."""
    subs = sorted(set(subjects))
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(subs))
    order = [subs[i] for i in perm]
    n = len(order)
    n_train = int(round(n * train_frac))
    n_val = int(round(n * val_frac))
    train = tuple(sorted(order[:n_train]))
    val = tuple(sorted(order[n_train:n_train + n_val]))
    test = tuple(sorted(order[n_train + n_val:]))
    return Split(train=train, val=val, test=test)


def seal_split(split: Split, seed: int, n_subjects: int) -> str:
    """Hash the split so any later change is detectable. Persisted to disk."""
    canon = json.dumps(
        {"seed": seed, "n_subjects": n_subjects, "split": split.to_dict()},
        sort_keys=True,
    )
    h = hashlib.sha256(canon.encode()).hexdigest()
    SEAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEAL_PATH.write_text(json.dumps({"seal": h, "seed": seed, "n_subjects": n_subjects,
                                     "split": split.to_dict()}, indent=2))
    return h


def verify_seal(split: Split, seed: int, n_subjects: int) -> bool:
    if not SEAL_PATH.exists():
        return False
    rec = json.loads(SEAL_PATH.read_text())
    return rec.get("seal") == hashlib.sha256(
        json.dumps({"seed": seed, "n_subjects": n_subjects, "split": split.to_dict()},
                   sort_keys=True).encode()).hexdigest()


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ``cosines`` now lives in causal_mind.utils.metrics (dependency-free) and is
# re-exported above for back-compat. Moved here to break the eval<->forecast
# circular import (CM-REPO S3).


def cosine_to_actual(pred: np.ndarray, actual: np.ndarray) -> float:
    return cosine(pred, actual)


def retrieval_rank(actual: np.ndarray, candidates: np.ndarray) -> int:
    """1-indexed rank of ``actual`` when candidates (incl. actual) are ranked by
    cosine to ``actual``. 1 = retrieved the true next thought first."""
    if len(candidates) == 0:
        return -1
    sims = np.array([cosine(actual, c) for c in candidates])
    order = np.argsort(-sims)
    # rank of the candidate that equals actual (first match)
    for rank, idx in enumerate(order, start=1):
        if np.allclose(candidates[idx], actual):
            return rank
    return len(candidates)


def category_accuracy(pred_cat: int, actual_cat: int) -> float:
    return 1.0 if pred_cat == actual_cat else 0.0


# --------------------------------------------------------------------------- #
# Uncertainty
# --------------------------------------------------------------------------- #
def bootstrap_ci(
    values: np.ndarray, n_boot: int = 2000, ci: float = 0.95, seed: int = 0
) -> tuple[float, float, float]:
    """Resample at the SUBJECT level is the caller's job; here we bootstrap the
    provided per-sample values (the analyses layer aggregates per subject first)."""
    v = np.asarray(values, dtype=float)
    if v.size == 0:
        return (float("nan"),) * 3
    rng = np.random.default_rng(seed)
    means = np.empty(n_boot)
    n = v.size
    for b in range(n_boot):
        means[b] = v[rng.integers(0, n, size=n)].mean()
    lo = np.percentile(means, 100 * (1 - ci) / 2)
    hi = np.percentile(means, 100 * (1 + ci) / 2)
    return (float(v.mean()), float(lo), float(hi))


def permutation_null_observed(observed: float, null: np.ndarray) -> float:
    """p-value: fraction of null stats >= observed (one-sided, bigger = better)."""
    null = np.asarray(null, dtype=float)
    if null.size == 0:
        return float("nan")
    return float((null >= observed).mean())
