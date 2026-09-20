"""CM-9A: agent policies O0-O10 (how the agent responds to the oracle).

Each policy is a callable: policy(world, signal, history) -> response vector.
`signal` is the oracle's revealed shift (array), "veto", or None (hidden).
`history` is a list of past (state, signal) pairs.
"""
from __future__ import annotations

from typing import Callable

import numpy as np


def _zero(world, signal, history) -> np.ndarray:
    return np.zeros(world.cfg.dim)


def _ignore(world, signal, history) -> np.ndarray:
    # the agent explicitly ignores the oracle's signal
    return np.zeros(world.cfg.dim)


def _trust(world, signal, history) -> np.ndarray:
    # fully follow the revealed shift
    if isinstance(signal, np.ndarray):
        return signal
    return np.zeros(world.cfg.dim)


def _partial(world, signal, history) -> np.ndarray:
    if isinstance(signal, np.ndarray):
        return 0.5 * signal
    return np.zeros(world.cfg.dim)


def _resist(world, signal, history) -> np.ndarray:
    # move away from the oracle's direction
    if isinstance(signal, np.ndarray):
        return -signal
    return np.zeros(world.cfg.dim)


def _explore(world, signal, history) -> np.ndarray:
    # add random exploration
    return 0.5 * world.rng.normal(size=world.cfg.dim)


def _exploit(world, signal, history) -> np.ndarray:
    # follow the oracle's suggestion scaled by its magnitude (confidence)
    if isinstance(signal, np.ndarray):
        mag = np.linalg.norm(signal)
        return np.clip(mag, 0.0, 1.0) * signal
    return np.zeros(world.cfg.dim)


def _game(world, signal, history) -> np.ndarray:
    # best response: move toward the revealed shift but dampen (Nash-like)
    if isinstance(signal, np.ndarray):
        return 0.7 * signal - 0.1 * world.x  # best response to the oracle
    return np.zeros(world.cfg.dim)


def _recursive(world, signal, history) -> np.ndarray:
    # predict the oracle's NEXT shift from the history of past shifts
    past = [s for _, s in history if isinstance(s, np.ndarray)]
    if past:
        pred = np.mean(past, axis=0)  # predict the next shift as the average
        return 0.5 * pred
    return np.zeros(world.cfg.dim)


def _adaptive(world, signal, history) -> np.ndarray:
    # learn the oracle's average behavior over time and respond to it
    past = [s for _, s in history if isinstance(s, np.ndarray)]
    if past:
        avg = np.mean(past, axis=0)
        return 0.6 * avg  # adapt to the oracle's typical shift
    return np.zeros(world.cfg.dim)


def _irreducible(world, signal, history) -> np.ndarray:
    # a complex, nonlinear, irreducible function of the state (no closed-form
    # simplification; the response cannot be reduced to a simple rule)
    x = world.x
    resp = np.tanh(0.5 * x) + 0.3 * np.sin(x) + 0.2 * (x ** 2 / (np.abs(x).sum() + 1e-9))
    if isinstance(signal, np.ndarray):
        resp = resp + 0.4 * signal
    return resp


POLICIES: dict[str, Callable] = {
    "O0": _zero,
    "O1": _ignore,
    "O2": _trust,
    "O3": _partial,
    "O4": _resist,
    "O5": _explore,
    "O6": _exploit,
    "O7": _game,
    "O8": _recursive,
    "O9": _adaptive,
    "O10": _irreducible,
}

POLICY_NAMES = list(POLICIES.keys())
