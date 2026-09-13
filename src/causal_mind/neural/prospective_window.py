"""HRF-safe prospective neural-window builder (CM-5).

The central methodological risk of CM-5 is HRF leakage: BOLD at time T integrates
neural activity from BEFORE T, and a naive "BOLD around thought t -> thought t+1"
alignment can include the target thought's own neural consequences.

Definition (frozen, see docs/protocol/cm5_frozen_protocol.md):
  For a target thought with MRI onset `o` (seconds):
      prediction_cutoff = o - B          (B = HRF-safe buffer, frozen 6 s)
      neural window     = BOLD volumes acquired in [o - B - W, o - B]
                          (W = neural history window, frozen 15 s)
  Every volume in the window is >= B seconds before the target onset, so it
  cannot yet reflect the target's own neural activity.

This module is BOLD-agnostic: it works on any volume time series + thought
onsets, so it is unit-tested on synthetic data and used on real fMRIPrep BOLD
once the derivatives are acquired.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

DEFAULT_BUFFER_S = 6.0    # frozen HRF-safe buffer (~4 TRs at TR=1.5 s)
DEFAULT_WINDOW_S = 15.0   # frozen neural history window (10 volumes)


def volume_times(tr: float, n_volumes: int) -> np.ndarray:
    """Acquisition time (seconds) of each BOLD volume (volume i at i*tr)."""
    return np.arange(n_volumes, dtype=float) * tr


def prediction_cutoff(target_onset: float, buffer_s: float) -> float:
    """Everything used as a feature must be available at or before this time."""
    if buffer_s < 0:
        raise ValueError("buffer_s must be >= 0")
    return target_onset - buffer_s


def neural_window_indices(vtimes: np.ndarray, target_onset: float,
                          buffer_s: float, window_s: float) -> list[int]:
    """Indices of BOLD volumes in [o - B - W, o - B] (all before the cutoff)."""
    if window_s <= 0:
        raise ValueError("window_s must be > 0")
    cutoff = prediction_cutoff(target_onset, buffer_s)
    lo = cutoff - window_s
    hi = cutoff
    return [int(i) for i, t in enumerate(vtimes) if lo <= t <= hi]


@dataclass
class NeuralWindow:
    target_onset: float
    cutoff: float
    volume_indices: list[int] = field(default_factory=list)
    buffer_s: float = DEFAULT_BUFFER_S
    window_s: float = DEFAULT_WINDOW_S

    @property
    def n_volumes(self) -> int:
        return len(self.volume_indices)

    def is_prospective(self, vtimes: np.ndarray) -> bool:
        """True iff every volume is strictly before the target onset (HRF-safe)."""
        return all(vtimes[i] < self.target_onset for i in self.volume_indices)


def build_neural_window(bold: np.ndarray, tr: float, target_onset: float,
                        buffer_s: float = DEFAULT_BUFFER_S,
                        window_s: float = DEFAULT_WINDOW_S) -> tuple[NeuralWindow, np.ndarray]:
    """Return (NeuralWindow, mean BOLD over the HRF-safe window).

    ``bold`` is (n_volumes, n_features). Raises if no volume falls in the safe
    window (e.g. a target too close to the start of the scan).
    """
    if bold.ndim != 2:
        raise ValueError("bold must be 2-D (n_volumes, n_features)")
    vtimes = volume_times(tr, bold.shape[0])
    idx = neural_window_indices(vtimes, target_onset, buffer_s, window_s)
    if not idx:
        raise ValueError(
            f"no BOLD volumes in the HRF-safe window for onset {target_onset:.2f}s "
            f"(cutoff {prediction_cutoff(target_onset, buffer_s):.2f}s)")
    win = NeuralWindow(target_onset=target_onset,
                       cutoff=prediction_cutoff(target_onset, buffer_s),
                       volume_indices=idx, buffer_s=buffer_s, window_s=window_s)
    assert_prospective(vtimes, win)
    return win, bold[idx].mean(axis=0)


def assert_prospective(vtimes: np.ndarray, win: NeuralWindow) -> None:
    """HARD contract: no window volume may be at/after the target onset, and none
    may be after the prediction cutoff. This is the anti-HRF-leakage guarantee."""
    for i in win.volume_indices:
        t = vtimes[i]
        if t >= win.target_onset:
            raise ValueError(
                f"volume {i} at {t:.2f}s is at/after target onset "
                f"{win.target_onset:.2f}s (HRF target contamination)")
        if t > win.cutoff:
            raise ValueError(
                f"volume {i} at {t:.2f}s is after prediction cutoff "
                f"{win.cutoff:.2f}s (post-cutoff leakage)")


def windows_for_subject(bold: np.ndarray, tr: float, onsets: np.ndarray,
                        buffer_s: float = DEFAULT_BUFFER_S,
                        window_s: float = DEFAULT_WINDOW_S) -> list[NeuralWindow]:
    """HRF-safe neural windows for every thought onset that has a valid window."""
    vtimes = volume_times(tr, bold.shape[0])
    out: list[NeuralWindow] = []
    for o in onsets:
        idx = neural_window_indices(vtimes, float(o), buffer_s, window_s)
        if not idx:
            continue
        win = NeuralWindow(target_onset=float(o),
                           cutoff=prediction_cutoff(float(o), buffer_s),
                           volume_indices=idx, buffer_s=buffer_s, window_s=window_s)
        assert_prospective(vtimes, win)
        out.append(win)
    return out
