from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SubjectSplit:
    train: tuple[str, ...]
    val: tuple[str, ...]
    test: tuple[str, ...]
    seed: int

    def subjects_of(self, split: str) -> frozenset[str]:
        return frozenset(getattr(self, split))

    def as_dict(self) -> dict[str, list[str]]:
        return {
            "train": list(self.train),
            "val": list(self.val),
            "test": list(self.test),
            "seed": [self.seed],
        }


def make_subject_disjoint_split(
    subjects: list[str],
    *,
    train_frac: float = 0.6,
    val_frac: float = 0.2,
    seed: int = 0,
) -> SubjectSplit:
    """Random subject-level split. Subjects never appear in two splits."""
    if not 0 < train_frac < 1 or not 0 < val_frac < 1 or train_frac + val_frac >= 1:
        raise ValueError("fractions must satisfy 0 < train_frac, val_frac and sum < 1")
    unique = sorted(set(subjects))
    if len(unique) < 3:
        raise ValueError("need at least 3 subjects for a 3-way split")
    rng = random.Random(seed)
    shuffled = unique[:]
    rng.shuffle(shuffled)
    n_train = max(1, round(len(shuffled) * train_frac))
    n_val = max(1, round(len(shuffled) * val_frac))
    n_train = min(n_train, len(shuffled) - 2)
    n_val = min(n_val, len(shuffled) - n_train - 1)
    return SubjectSplit(
        train=tuple(shuffled[:n_train]),
        val=tuple(shuffled[n_train : n_train + n_val]),
        test=tuple(shuffled[n_train + n_val :]),
        seed=seed,
    )


def repeated_splits(
    subjects: list[str],
    n: int = 5,
    *,
    base_seed: int = 0,
    train_frac: float = 0.6,
    val_frac: float = 0.2,
) -> list[SubjectSplit]:
    return [
        make_subject_disjoint_split(
            subjects, train_frac=train_frac, val_frac=val_frac, seed=base_seed + i
        )
        for i in range(n)
    ]


@dataclass
class SplitViolations:
    shared_subjects: dict[str, str] = field(default_factory=dict)  # subject -> "splitA/splitB"
    unknown_subjects: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.shared_subjects and not self.unknown_subjects


def validate_split_integrity(
    split: SubjectSplit,
    sample_subjects: list[str],
) -> SplitViolations:
    """Check that no subject appears in two splits and all samples map to a split."""
    seen: dict[str, str] = {}
    violations = SplitViolations()
    for name, group in (("train", split.train), ("val", split.val), ("test", split.test)):
        for subject in group:
            if subject in seen:
                violations.shared_subjects[subject] = f"{seen[subject]}/{name}"
            else:
                seen[subject] = name
    all_splits = frozenset(split.train) | frozenset(split.val) | frozenset(split.test)
    for subject in sample_subjects:
        if subject not in all_splits:
            violations.unknown_subjects.append(subject)
    return violations


def check_temporal_crossing(
    subject_order: dict[str, list[str]],
    split: SubjectSplit,
) -> list[str]:
    """Return subjects whose samples are split across groups (should be impossible for
    subject-disjoint splits; guards against row-level leakage bugs)."""
    assignments: dict[str, str] = {}
    for name, group in (("train", split.train), ("val", split.val), ("test", split.test)):
        for subject in group:
            assignments[subject] = name
    crossings: list[str] = []
    for subject, sample_ids in subject_order.items():
        groups = {assignments.get(s) for s in sample_ids}
        groups.discard(None)
        if len(groups) > 1:
            crossings.append(subject)
    return crossings
