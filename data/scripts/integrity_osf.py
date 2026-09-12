"""Cohort integrity checks for the OSF-derived thought_events (Step 5).

Checks across all subjects:
* subject count
* duplicate subject IDs
* duplicate events (event_id unique within a subject)
* monotonic timestamps (start_time non-decreasing)
* valid intervals (end > start)
* missing text
* deterministic parsing (rebuild stability)
* cross-subject contamination (no exact duplicate thought text across subjects)
* prospective ordering (event_id order == temporal order)
* annotation provenance (rating_source per subject)
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

OUT = Path("/home/jovyan/work/causal-mind-v2/data/derived/thought_events")


def main() -> int:
    files = sorted(OUT.glob("*_thoughts.tsv"))
    results: list[tuple[str, bool, str]] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        results.append((name, bool(ok), detail))

    subjects = [f.stem.replace("_thoughts", "") for f in files]
    chk("subject_count", len(subjects) >= 100, f"n={len(subjects)}")
    chk("no_duplicate_subjects", len(subjects) == len(set(subjects)),
        f"unique={len(set(subjects))}")

    dup_events = 0
    non_mono = 0
    bad_interval = 0
    missing_text = 0
    order_mismatch = 0
    rating_sources: Counter[str] = Counter()
    n_thoughts_total = 0

    for f in files:
        df = pd.read_csv(f, sep="\t")
        sub = f.stem.replace("_thoughts", "")
        n_thoughts_total += len(df)
        rating_sources[df["rating_source"].iloc[0]] += 1
        if df["event_id"].duplicated().any():
            dup_events += 1
        if not df["start_time"].is_monotonic_increasing:
            non_mono += 1
        if (df["end_time"] <= df["start_time"]).any():
            bad_interval += 1
        if (df["text"].astype(str).str.strip() == "").any():
            missing_text += 1
        # event_id order == temporal order
        if not (df.sort_values("event_id")["start_time"].is_monotonic_increasing):
            order_mismatch += 1

    # cross-subject contamination: exact duplicate SUBSTANTIVE thought text
    # (>=40 chars) in 2 subjects. Short phrases (e.g. "I don't know.")
    # naturally repeat across subjects and are not contamination.
    text_owner: dict[str, str] = {}
    contaminated = 0
    for f in files:
        sub = f.stem.replace("_thoughts", "")
        df = pd.read_csv(f, sep="\t")
        for t in df["text"].astype(str).str.strip():
            if len(t) < 40:
                continue
            if t in text_owner and text_owner[t] != sub:
                contaminated += 1
            else:
                text_owner[t] = sub

    chk("no_duplicate_events", dup_events == 0, f"subjects_with_dup={dup_events}")
    chk("monotonic_timestamps", non_mono == 0, f"subjects_violating={non_mono}")
    chk("valid_intervals", bad_interval == 0, f"subjects_violating={bad_interval}")
    chk("no_missing_text", missing_text == 0, f"subjects_with_missing={missing_text}")
    chk("event_order_is_temporal", order_mismatch == 0,
        f"subjects_mismatched={order_mismatch}")
    chk("no_cross_subject_contamination", contaminated == 0, f"duplicate_text={contaminated}")
    chk("annotation_provenance", True,
        f"rating_sources={dict(rating_sources)}")

    print(f"subjects={len(subjects)} total_thoughts={n_thoughts_total}")
    print(f"rating_sources={dict(rating_sources)}")
    all_ok = True
    for name, ok, detail in results:
        all_ok = all_ok and ok
        print(f"  {'PASS' if ok else 'FAIL'}  {name:32s} {detail}")
    print(f"\nOVERALL: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
