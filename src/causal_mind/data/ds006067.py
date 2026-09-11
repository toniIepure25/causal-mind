"""Minimal loader for the OpenNeuro ds006067 (ThinkAloud) subset.

Maps  subject -> run -> BOLD timeline -> transcript/thought events -> annotations
and provides explicit temporal-alignment queries. Read-only over the raw data.

Data layout (under ``data_root``, default the central raw dir):
    sub-XXX/func/sub-XXX_task-thinkaloud_events.tsv      # transcript (onset/duration/transcript)
    derivatives/sub-XXX/func/..._space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz
    derivatives/sub-XXX/func/..._desc-confounds_timeseries.tsv
    derivatives/sub-XXX/anat/sub-XXX_desc-preproc_T1w.nii.gz
    participants.tsv, dataset_description.json, task-thinkaloud_bold.json

Alignment convention (see docs/datasets/ds006067_alignment.md):
    * time zero: events.tsv onset=0  <->  BOLD volume 1 (t=0); both in seconds.
    * volume k (1-indexed) spans [(k-1)*TR, k*TR).
    * thought i spans [onset_i, onset_i + duration_i).
    * HRF is NOT applied here; any HRF handling is an explicit CM-2/CM-3 modeling choice.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

DEFAULT_DATA_ROOT = Path("/home/jovyan/work/causal-mind-v2/data/raw/ds006067")

_MNI = "space-MNI152NLin2009cAsym"
BOLD_REL = f"{{sub}}/func/{{sub}}_task-thinkaloud_{_MNI}_desc-preproc_bold.nii.gz"
BOLD_JSON_REL = "{sub}/func/{sub}_task-thinkaloud_bold.json"
CONF_REL = f"{{sub}}/func/{{sub}}_task-thinkaloud_{_MNI}_confounds_timeseries.tsv"
T1W_REL = "{sub}/anat/{sub}_T1w.nii.gz"
EVENTS_REL = "{sub}/func/{sub}_task-thinkaloud_events.tsv"


@dataclass(frozen=True)
class ThoughtEvent:
    """One thought / spoken sentence with a time interval (seconds)."""

    index: int
    onset: float
    duration: float
    transcript: str

    @property
    def end(self) -> float:
        return self.onset + self.duration

    @property
    def id(self) -> str:
        return f"ev-{self.index:04d}"


@dataclass
class Run:
    subject: str
    tr: float
    n_volumes: int
    events: list[ThoughtEvent] = field(default_factory=list)
    bold_path: Path | None = None
    bold_shape: tuple[int, ...] | None = None  # (x, y, z, t) when header loaded
    confound_n_rows: int | None = None

    @property
    def duration_s(self) -> float:
        return self.n_volumes * self.tr

    # -- temporal alignment -------------------------------------------------
    def volume_time(self, k: int) -> float:
        """Onset time (s) of 1-indexed volume k."""
        if not 1 <= k <= self.n_volumes:
            raise ValueError(f"volume {k} out of range 1..{self.n_volumes}")
        return (k - 1) * self.tr

    def time_to_volume(self, t: float) -> int:
        """1-indexed volume index containing time t (clipped to run bounds)."""
        k = int(t // self.tr) + 1
        return max(1, min(k, self.n_volumes))

    def events_overlapping_volume(self, k: int) -> list[ThoughtEvent]:
        """Thoughts whose interval intersects volume k's half-open time window."""
        lo, hi = self.volume_time(k), self.volume_time(k) + self.tr
        return [e for e in self.events if e.onset < hi and e.end > lo]

    def bold_window_for_event(self, e: ThoughtEvent) -> tuple[int, int]:
        """(first_vol, last_vol) 1-indexed BOLD window overlapping a thought."""
        first = self.time_to_volume(e.onset)
        last = self.time_to_volume(max(e.end - 1e-9, e.onset))
        return first, max(first, last)

    def verbal_gaps(self, min_gap_s: float = 0.0) -> list[tuple[float, float]]:
        """Silent gaps (start, end) between consecutive thoughts."""
        gaps = []
        for a, b in zip(self.events, self.events[1:], strict=False):
            if b.onset - a.end > min_gap_s:
                gaps.append((a.end, b.onset))
        return gaps

    def verbal_overlaps(self) -> list[tuple[int, int]]:
        """Pairs of (index_a, index_b) where one thought starts before the prior ends."""
        out = []
        for a, b in zip(self.events, self.events[1:], strict=False):
            if b.onset < a.end:
                out.append((a.index, b.index))
        return out


# -- loading ----------------------------------------------------------------
def list_subjects(data_root: Path = DEFAULT_DATA_ROOT) -> list[str]:
    import re

    pat = re.compile(r"^sub-\d+$")
    subs = sorted(p.name for p in Path(data_root).glob("sub-*") if p.is_dir() and pat.match(p.name))
    return subs


def load_events(sub: str, data_root: Path = DEFAULT_DATA_ROOT) -> list[ThoughtEvent]:
    path = Path(data_root) / EVENTS_REL.format(sub=sub)
    events: list[ThoughtEvent] = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for i, row in enumerate(reader):
            events.append(
                ThoughtEvent(
                    index=i,
                    onset=float(row["onset"]),
                    duration=float(row["duration"]),
                    transcript=row["transcript"],
                )
            )
    return events


def _read_tr(sub: str, data_root: Path) -> float:
    candidates = [
        Path(data_root) / BOLD_JSON_REL.format(sub=sub),
        Path(data_root) / f"{sub}/func/{sub}_task-thinkaloud_bold.json",
        Path(data_root) / "task-thinkaloud_bold.json",  # task-level TR (shared)
    ]
    for p in candidates:
        if p.exists():
            with open(p, encoding="utf-8") as fh:
                return float(json.load(fh)["RepetitionTime"])
    raise FileNotFoundError(f"no sidecar with RepetitionTime for {sub} under {data_root}")


def load_run(
    sub: str,
    data_root: Path = DEFAULT_DATA_ROOT,
    load_bold: bool = False,
) -> Run:
    """Load a subject's run. ``load_bold=True`` loads the full BOLD 4D array (large)."""
    data_root = Path(data_root)
    tr = _read_tr(sub, data_root)
    bold_path = data_root / BOLD_REL.format(sub=sub)
    run = Run(subject=sub, tr=tr, n_volumes=0, bold_path=bold_path)

    if bold_path.exists():
        import nibabel as nib

        img = nib.load(str(bold_path))
        run.bold_shape = tuple(img.shape)
        run.n_volumes = int(img.shape[-1])
        if load_bold:
            run.bold_data = np.asanyarray(img.dataobj)  # type: ignore[attr-defined]

    # Cross-check volume count against the confounds timeseries when present.
    conf = data_root / CONF_REL.format(sub=sub)
    if conf.exists():
        with open(conf, encoding="utf-8") as fh:
            run.confound_n_rows = sum(1 for _ in fh) - 1

    run.events = load_events(sub, data_root)
    return run


def load_participants(data_root: Path = DEFAULT_DATA_ROOT) -> dict[str, dict]:
    path = Path(data_root) / "participants.tsv"
    out: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            out[row["participant_id"]] = {
                "age": int(row["age"]),
                "sex": row["sex"],
            }
    return out


# -- integrity checks -------------------------------------------------------
def check_monotonic(events: list[ThoughtEvent]) -> list[int]:
    """Indices of events whose onset is not strictly after the previous onset."""
    bad = []
    for prev, cur in zip(events, events[1:], strict=False):
        if cur.onset <= prev.onset:
            bad.append(cur.index)
    return bad


def check_no_duplicate_ids(events: list[ThoughtEvent]) -> list[str]:
    seen: set[str] = set()
    dups = []
    for e in events:
        if e.id in seen:
            dups.append(e.id)
        seen.add(e.id)
    return dups


def check_impossible_ranges(events: list[ThoughtEvent]) -> list[int]:
    """Events with non-positive duration or end before onset (impossible)."""
    return [e.index for e in events if e.duration <= 0 or e.end < e.onset]


def check_within_run(run: Run, tol_s: float = 15.0) -> list[int]:
    """Events whose interval starts after the BOLD run ends (beyond tol)."""
    return [e.index for e in run.events if e.onset > run.duration_s + tol_s]


def check_deterministic(sub: str, data_root: Path = DEFAULT_DATA_ROOT) -> bool:
    a = load_events(sub, data_root)
    b = load_events(sub, data_root)
    return [ (e.index, e.onset, e.duration, e.transcript) for e in a ] == [
        (e.index, e.onset, e.duration, e.transcript) for e in b
    ]


# -- subject-disjoint splits ------------------------------------------------
def subject_disjoint_split(
    subjects: list[str],
    test_frac: float = 0.2,
    val_frac: float = 0.2,
    seed: int = 0,
) -> dict[str, list[str]]:
    """Deterministic subject-disjoint train/val/test split (never splits a subject)."""
    if not 0 < test_frac < 1 or not 0 < val_frac < 1 or test_frac + val_frac >= 1:
        raise ValueError("fractions must be in (0,1) and test_frac+val_frac < 1")
    rng = np.random.default_rng(seed)
    order = list(subjects)
    rng.shuffle(order)
    n = len(order)
    n_test = max(1, int(round(n * test_frac)))
    n_val = max(1, int(round(n * val_frac)))
    n_test = min(n_test, n - 2)
    n_val = min(n_val, n - n_test - 1)
    return {
        "test": order[:n_test],
        "val": order[n_test : n_test + n_val],
        "train": order[n_test + n_val :],
    }
