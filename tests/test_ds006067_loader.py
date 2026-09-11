"""Integrity + alignment tests for the ds006067 loader (CM-1).

Run against the fetched minimal subset (sub-001, sub-005) under the central raw
dir. Skips cleanly if the data is not present (e.g. a fresh clone before download).
"""
from __future__ import annotations

import pytest

from causal_mind.data import ds006067 as L

DATA = L.DEFAULT_DATA_ROOT
_HAS_DATA = (DATA / "participants.tsv").exists()
pytestmark = pytest.mark.skipif(not _HAS_DATA, reason="ds006067 subset not downloaded")


@pytest.fixture(scope="module")
def run001() -> L.Run:
    return L.load_run("sub-001", DATA)


@pytest.fixture(scope="module")
def run005() -> L.Run:
    return L.load_run("sub-005", DATA)


# -- identity & structure ---------------------------------------------------
def test_subject_identity(run001):
    assert run001.subject == "sub-001"
    assert run001.bold_path is not None and run001.bold_path.exists()


def test_run_identity_and_tr(run001):
    assert run001.tr == pytest.approx(1.5)
    assert run001.n_volumes == 400
    assert run001.duration_s == pytest.approx(600.0)


def test_bold_shape_is_4d(run001):
    assert run001.bold_shape is not None
    assert len(run001.bold_shape) == 4
    assert run001.bold_shape[-1] == 400


def test_confounds_match_volumes(run001):
    assert run001.confound_n_rows == 400
    assert run001.confound_n_rows == run001.n_volumes


def test_events_loaded(run001):
    assert len(run001.events) > 50
    assert all(e.transcript.strip() for e in run001.events)


def test_participants(run001):
    p = L.load_participants(DATA)
    assert "sub-001" in p and "sub-005" in p
    assert p["sub-001"]["sex"] in {"M", "F"}
    assert 10 <= p["sub-001"]["age"] <= 90


# -- timestamp integrity ----------------------------------------------------
def test_monotonic_onsets(run001):
    assert L.check_monotonic(run001.events) == []


def test_no_duplicate_event_ids(run001):
    assert L.check_no_duplicate_ids(run001.events) == []


def test_no_impossible_time_ranges(run001):
    assert L.check_impossible_ranges(run001.events) == []


def test_no_event_starts_after_run(run001):
    # No thought begins after the 600 s BOLD run (tolerance 15 s).
    assert L.check_within_run(run001, tol_s=15.0) == []


def test_deterministic_parsing():
    assert L.check_deterministic("sub-001", DATA) is True


# -- temporal alignment -----------------------------------------------------
def test_volume_time_grid(run001):
    assert run001.volume_time(1) == pytest.approx(0.0)
    assert run001.volume_time(400) == pytest.approx(399 * 1.5)
    with pytest.raises(ValueError):
        run001.volume_time(0)
    with pytest.raises(ValueError):
        run001.volume_time(401)


def test_time_to_volume_roundtrip(run001):
    assert run001.time_to_volume(0.0) == 1
    assert run001.time_to_volume(598.5) == 400
    for k in (1, 100, 400):
        t = run001.volume_time(k)
        assert run001.time_to_volume(t) == k


def test_first_volume_has_no_speech(run001):
    # First thought of sub-001 starts at ~9.6 s, so volume 1 (0-1.5 s) is silent.
    assert run001.events[0].onset > 1.5
    assert run001.events_overlapping_volume(1) == []


def test_event_maps_to_bold_window(run001):
    e = run001.events[0]
    first, last = run001.bold_window_for_event(e)
    assert 1 <= first <= last <= 400
    # The event onset must fall inside volume `first`'s window.
    lo = run001.volume_time(first)
    assert lo <= e.onset < lo + run001.tr


def test_overlap_query_is_consistent(run001):
    # Every event must be reported as overlapping at least the volume at its onset.
    for e in run001.events[:20]:
        k = run001.time_to_volume(e.onset)
        assert e in run001.events_overlapping_volume(k)


def test_gaps_and_overlaps_well_formed(run001):
    gaps = run001.verbal_gaps()
    assert isinstance(gaps, list)
    assert all(start < end for start, end in gaps)
    overlaps = run001.verbal_overlaps()
    assert isinstance(overlaps, list)
    # Clean think-aloud: thoughts are sequential, so no true overlaps expected.
    assert overlaps == []


# -- second subject sanity --------------------------------------------------
def test_second_subject_loads(run005):
    assert run005.subject == "sub-005"
    assert run005.n_volumes == 400
    assert L.check_monotonic(run005.events) == []
    assert L.check_no_duplicate_ids(run005.events) == []


# -- subject-disjoint split -------------------------------------------------
def test_subject_disjoint_split_properties():
    # Pure function: exercise with a synthetic cohort (independent of download size).
    subjects = [f"sub-{i:03d}" for i in range(1, 21)]
    split = L.subject_disjoint_split(subjects, test_frac=0.2, val_frac=0.2, seed=0)
    train, val, test = split["train"], split["val"], split["test"]
    # pairwise disjoint
    assert not (set(train) & set(val))
    assert not (set(train) & set(test))
    assert not (set(val) & set(test))
    # full coverage, no fabrication
    assert set(train) | set(val) | set(test) == set(subjects)
    # non-empty
    assert train and val and test
    # deterministic
    again = L.subject_disjoint_split(subjects, test_frac=0.2, val_frac=0.2, seed=0)
    assert again == split
    # different seed can differ but must stay valid
    other = L.subject_disjoint_split(subjects, seed=1)
    assert set(other["train"]) | set(other["val"]) | set(other["test"]) == set(subjects)
