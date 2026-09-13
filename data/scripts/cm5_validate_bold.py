"""Validate the fMRIPrep MNI BOLD derivatives for CM-5 (before modeling).

Prospective checks (no outcome inspection):
- BOLD is 4-D (n_volumes, nx, ny, nz) with a plausible volume count.
- RepetitionTime (TR) from the sidecar JSON matches the expected ~1.5 s.
- Space is MNI152NLin2009cAsym (the required MNI space).
- Every event onset (events.tsv) falls inside the scan [0, n_volumes*TR).
- The confounds timeseries has one row per volume.

Pure validation functions are unit-tested; main() loads the on-disk files.
Run: python data/scripts/cm5_validate_bold.py --subject sub-001 --derivatives <dir>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

EXPECTED_SPACE = "MNI152NLin2009cAsym"
EXPECTED_TR = 1.5


def validate_bold_shape(shape: tuple[int, ...]) -> tuple[int | None, list[str]]:
    issues: list[str] = []
    if len(shape) != 4:
        issues.append(f"BOLD must be 4-D, got {len(shape)}-D")
        return None, issues
    n_vol = int(shape[0])
    if n_vol < 100:
        issues.append(f"unexpectedly few volumes: {n_vol}")
    return n_vol, issues


def validate_tr(tr: float | None) -> list[str]:
    issues: list[str] = []
    if tr is None:
        issues.append("RepetitionTime missing from sidecar JSON")
    elif abs(tr - EXPECTED_TR) > 0.05:
        issues.append(f"TR {tr} != expected {EXPECTED_TR}")
    return issues


def validate_space(space: str | None) -> list[str]:
    issues: list[str] = []
    if space != EXPECTED_SPACE:
        issues.append(f"Space {space!r} != {EXPECTED_SPACE!r}")
    return issues


def validate_events(onsets: np.ndarray, n_volumes: int, tr: float) -> list[str]:
    issues: list[str] = []
    dur = n_volumes * tr
    for o in onsets:
        if o < 0 or o >= dur:
            issues.append(f"onset {o:.2f} s outside scan [0, {dur:.2f})")
    return issues


def validate_confounds(n_conf_rows: int, n_volumes: int) -> list[str]:
    issues: list[str] = []
    if n_conf_rows != n_volumes:
        issues.append(f"confounds rows {n_conf_rows} != n_volumes {n_volumes}")
    return issues


def load_events_onsets(events_tsv: Path) -> np.ndarray:
    txt = events_tsv.read_text(encoding="utf-8")
    header = txt.splitlines()[0].split("\t")
    i = header.index("onset")
    onsets = [float(line.split("\t")[i]) for line in txt.splitlines()[1:] if line.strip()]
    return np.asarray(onsets, dtype=float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", required=True)
    ap.add_argument("--derivatives", required=True, help="derivatives dir (ds006067)")
    ap.add_argument("--raw", required=True, help="raw BIDS dir (for events.tsv)")
    args = ap.parse_args()

    import nibabel as nib

    sub = args.subject
    d = Path(args.derivatives) / sub / "func"
    bold_path = d / f"{sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    json_path = bold_path.with_suffix(".json")
    conf_path = d / f"{sub}_task-thinkaloud_desc-confounds_timeseries.tsv"
    events_path = Path(args.raw) / sub / "func" / f"{sub}_task-thinkaloud_events.tsv"

    issues: list[str] = []
    img = nib.load(str(bold_path))
    shape = img.shape
    n_vol, shape_issues = validate_bold_shape(shape)
    issues += shape_issues

    meta = json.loads(json_path.read_text(encoding="utf-8"))
    issues += validate_tr(meta.get("RepetitionTime"))
    issues += validate_space(meta.get("Space"))

    if n_vol is not None:
        tr = meta.get("RepetitionTime", EXPECTED_TR)
        onsets = load_events_onsets(events_path)
        issues += validate_events(onsets, n_vol, tr)
        conf_txt = conf_path.read_text(encoding="utf-8").splitlines()
        issues += validate_confounds(len(conf_txt) - 1, n_vol)

    print(f"subject={sub} shape={shape} n_volumes={n_vol}")
    print(f"TR={meta.get('RepetitionTime')} Space={meta.get('Space')}")
    if issues:
        print("ISSUES:")
        for i in issues:
            print(f"  - {i}")
        raise SystemExit(1)
    print("BOLD VALIDATION PASS")


if __name__ == "__main__":
    main()
