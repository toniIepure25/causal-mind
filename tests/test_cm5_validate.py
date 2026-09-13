"""Tests for the CM-5 BOLD validation functions (pure, synthetic inputs)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data" / "scripts"))
from cm5_validate_bold import (
    validate_bold_shape,
    validate_confounds,
    validate_events,
    validate_space,
    validate_tr,
)


def test_bold_shape_ok():
    n_vol, issues = validate_bold_shape((600, 91, 109, 91))
    assert n_vol == 600
    assert issues == []


def test_bold_shape_bad_dims():
    n_vol, issues = validate_bold_shape((91, 109, 91))
    assert n_vol is None
    assert any("4-D" in i for i in issues)


def test_bold_shape_few_volumes():
    n_vol, issues = validate_bold_shape((50, 91, 109, 91))
    assert n_vol == 50
    assert any("few volumes" in i for i in issues)


def test_tr_ok_and_bad():
    assert validate_tr(1.5) == []
    assert validate_tr(None) != []
    assert validate_tr(2.0) != []


def test_space_ok_and_bad():
    assert validate_space("MNI152NLin2009cAsym") == []
    assert validate_space("T1w") != []
    assert validate_space(None) != []


def test_events_within_scan():
    onsets = np.array([0.0, 10.0, 890.0])
    assert validate_events(onsets, n_volumes=600, tr=1.5) == []
    # 600 * 1.5 = 900 s; onset 950 is outside
    assert validate_events(np.array([950.0]), 600, 1.5) != []


def test_confounds_row_count():
    assert validate_confounds(600, 600) == []
    assert validate_confounds(599, 600) != []


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
