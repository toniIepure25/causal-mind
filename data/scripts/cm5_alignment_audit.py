#!/usr/bin/env python3
"""Cohort-level alignment audit (N-GATE 1 post-hoc verification).

For every eligible subject, verify the OSF thought stream's first event
start_time equals the raw MRI events.tsv first onset (the MRI time base), and
that the OSF stream is monotonic and within the 600 s scan. This confirms the
MRI<->OSF time-base equality at cohort level (previously spot-checked on 2
subjects).
"""
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
from causal_mind.data import osf_a56rm

GIT = "/home/jovyan/work/ds006067_git"
import json
seal = json.load(open("/home/jovyan/work/causal-mind-v2/reports/cm5_cohort_seal.json"))
subs = (seal["included_subjects"]["train"] + seal["included_subjects"]["val"]
        + seal["included_subjects"]["test"])

rows = []
for sub in subs:
    raw = pd.read_csv(f"{GIT}/{sub}/func/{sub}_task-thinkaloud_events.tsv", sep="\t")
    osf = osf_a56rm.load_thought_events(sub)
    raw_first = float(raw["onset"].iloc[0])
    osf_first = float(osf[0]["onset"])
    diff = osf_first - raw_first
    osf_starts = np.array([e["onset"] for e in osf])
    mono = bool(np.all(np.diff(osf_starts) > 0))
    in_range = bool(osf_starts.min() >= 0 and osf_starts.max() <= 600)
    rows.append([sub, round(raw_first, 3), round(osf_first, 3), round(diff, 4),
                 int(mono), int(in_range), len(osf)])

df = pd.DataFrame(rows, columns=["subject", "raw_first_onset", "osf_first_start",
                                 "diff_s", "monotonic", "in_range", "n_thoughts"])
df.to_csv("/home/jovyan/work/causal-mind-v2/reports/cm5_alignment_audit.tsv",
          sep="\t", index=False)
print(f"subjects: {len(df)}")
print(f"first-event |diff|: max={df['diff_s'].abs().max():.4f}s  "
      f"mean={df['diff_s'].abs().mean():.4f}s")
print(f"monotonic: {int(df['monotonic'].sum())}/{len(df)}  "
      f"in_range: {int(df['in_range'].sum())}/{len(df)}")
bad = df[df["diff_s"].abs() > 0.5]
if len(bad):
    print("subjects with first-event diff > 0.5s:")
    print(bad.to_string(index=False))
else:
    print("all first-event alignments within 0.5s")
print("wrote reports/cm5_alignment_audit.tsv")
