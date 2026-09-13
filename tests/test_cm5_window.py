"""Unit tests for the HRF-safe prospective neural-window builder (CM-5).

These run on synthetic BOLD (no fMRI content required) and enforce the
anti-HRF-leakage contract: no neural feature may come from a volume at/after the
target onset or after the prediction cutoff.
"""
from __future__ import annotations

import numpy as np
import pytest

from causal_mind.neural.prospective_window import (
    NeuralWindow,
    assert_prospective,
    build_neural_window,
    neural_window_indices,
    prediction_cutoff,
    volume_times,
    windows_for_subject,
)

TR = 1.5
B = 6.0
W = 15.0
N = 400  # 600 s scan


def test_prediction_cutoff_is_onset_minus_buffer():
    assert prediction_cutoff(100.0, B) == pytest.approx(94.0)
    with pytest.raises(ValueError):
        prediction_cutoff(100.0, -1.0)


def test_window_is_within_safe_bounds():
    vtimes = volume_times(TR, N)
    o = 100.0
    idx = neural_window_indices(vtimes, o, B, W)
    assert idx, "expected volumes in the safe window"
    ts = vtimes[idx]
    # all volumes in [o - B - W, o - B]
    assert ts.min() >= o - B - W - 1e-9
    assert ts.max() <= o - B + 1e-9
    # and strictly before the target onset (HRF-safe)
    assert ts.max() < o


def test_window_mean_is_correct_on_synthetic_bold():
    # bold[volume] = volume index, so the window mean is the mean index
    bold = np.arange(N, dtype=float).reshape(-1, 1)
    o = 100.0
    win, feat = build_neural_window(bold, TR, o, B, W)
    expected = float(np.mean([i for i in win.volume_indices]))
    assert feat[0] == pytest.approx(expected)
    assert win.is_prospective(volume_times(TR, N))


def test_target_near_start_raises():
    bold = np.ones((N, 4))
    # onset 3 s: cutoff = -3 s -> no valid prior window
    with pytest.raises(ValueError):
        build_neural_window(bold, TR, 3.0, B, W)


def test_assert_prospective_rejects_post_onset_volume():
    vtimes = volume_times(TR, N)
    # a window that (wrongly) includes a volume at/after the onset must be rejected
    # 67 * 1.5 = 100.5 >= 100 (target onset) -> HRF target contamination
    bad = NeuralWindow(target_onset=100.0, cutoff=94.0,
                       volume_indices=[67], buffer_s=B, window_s=W)
    with pytest.raises(ValueError):
        assert_prospective(vtimes, bad)


def test_windows_for_subject_skips_invalid():
    bold = np.ones((N, 4))
    # the window is [o - B - W, o - B]; it has a volume only if o - B >= 0,
    # i.e. onset >= B (6 s). The window is always BEFORE the onset, so being
    # near the end of the scan is still valid.
    onsets = np.array([3.0, 5.0, 10.0, 50.0, 100.0, 590.0])
    wins = windows_for_subject(bold, TR, onsets, B, W)
    onsets_used = [w.target_onset for w in wins]
    assert 3.0 not in onsets_used
    assert 5.0 not in onsets_used
    assert 10.0 in onsets_used
    assert 100.0 in onsets_used
    assert 590.0 in onsets_used
    for w in wins:
        assert w.is_prospective(volume_times(TR, N))


def test_larger_buffer_excludes_more_recent_volumes():
    vtimes = volume_times(TR, N)
    o = 100.0
    idx_small = neural_window_indices(vtimes, o, B, W)      # B=6
    idx_large = neural_window_indices(vtimes, o, 12.0, W)  # B=12
    # a larger buffer pushes the whole window earlier (more conservative)
    assert vtimes[idx_large].max() < vtimes[idx_small].max()
