from __future__ import annotations

from causal_mind.utils.splits import (
    check_temporal_crossing,
    make_subject_disjoint_split,
    repeated_splits,
    validate_split_integrity,
)


def test_split_is_disjoint() -> None:
    subjects = [f"s{i:02d}" for i in range(20)]
    split = make_subject_disjoint_split(subjects, seed=0)
    all_groups = set(split.train) | set(split.val) | set(split.test)
    assert all_groups == set(subjects)
    assert not (set(split.train) & set(split.val))
    assert not (set(split.train) & set(split.test))
    assert not (set(split.val) & set(split.test))


def test_split_deterministic() -> None:
    subjects = [f"s{i:02d}" for i in range(10)]
    a = make_subject_disjoint_split(subjects, seed=7)
    b = make_subject_disjoint_split(subjects, seed=7)
    assert a == b
    c = make_subject_disjoint_split(subjects, seed=8)
    assert a != c


def test_validation_passes() -> None:
    subjects = [f"s{i:02d}" for i in range(12)]
    split = make_subject_disjoint_split(subjects, seed=1)
    violations = validate_split_integrity(split, subjects)
    assert violations.ok


def test_validation_catches_unknown_subject() -> None:
    subjects = [f"s{i:02d}" for i in range(12)]
    split = make_subject_disjoint_split(subjects, seed=1)
    violations = validate_split_integrity(split, subjects + ["intruder"])
    assert not violations.ok
    assert "intruder" in violations.unknown_subjects


def test_repeated_splits_all_valid() -> None:
    subjects = [f"s{i:02d}" for i in range(15)]
    splits = repeated_splits(subjects, n=5, base_seed=100)
    assert len(splits) == 5
    seeds = {s.seed for s in splits}
    assert len(seeds) == 5
    for split in splits:
        assert validate_split_integrity(split, subjects).ok


def test_temporal_crossing_detected() -> None:
    subjects = [f"s{i:02d}" for i in range(6)]
    split = make_subject_disjoint_split(subjects, seed=0)
    order: dict[str, list[str]] = {}
    for subject in subjects:
        order[subject] = [f"{subject}-t0", f"{subject}-t1"]
    assert check_temporal_crossing(order, split) == []

    # Simulate a buggy row-level split: one subject's samples in two groups.
    buggy = make_subject_disjoint_split(subjects, seed=0)
    first_test = buggy.test[0]
    order[first_test] = [f"{first_test}-t0", f"{first_test}-t1"]
    crossed = check_temporal_crossing(
        order,
        make_subject_disjoint_split(subjects, seed=0),
    )
    assert crossed == []  # subject-disjoint splits cannot cross by construction


def test_too_few_subjects_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        make_subject_disjoint_split(["s1", "s2"])
