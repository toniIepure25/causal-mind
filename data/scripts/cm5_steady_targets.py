#!/usr/bin/env python3
"""Recompute HRF-safe target counts under the steady-state amendment.

AM-1: primary target requires onset >= N_NONSTEADY*TR + B + W = 15+6+15 = 36 s
so the entire neural window [o-B-W, o-B] lies in steady-state BOLD.
Compares the 21 s (frozen) vs 36 s (amended) definitions.
"""
import sys
from pathlib import Path

sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
from causal_mind.data.osf_a56rm import load_thought_events  # noqa: E402

B, W, TR, N_NS = 6.0, 15.0, 1.5, 10
SCAN = 400 * TR
ONSET_FROZEN = B + W            # 21 s
ONSET_STEADY = N_NS * TR + B + W  # 36 s

subs = [f"sub-{i:03d}" for i in range(1, 128)
        if Path(f"/home/jovyan/work/causal-mind-v2/data/derived/thought_events/{f'sub-{i:03d}'}_thoughts.tsv").exists()]
rows = []
for sub in subs:
    evs = load_thought_events(sub)
    spans = [(e["onset"], e["duration"]) for e in evs]
    n21 = sum(1 for s, d in spans if s >= ONSET_FROZEN and s + d <= SCAN)
    n36 = sum(1 for s, d in spans if s >= ONSET_STEADY and s + d <= SCAN)
    rows.append((sub, n21, n36))

import statistics as st
c21 = [r[1] for r in rows]
c36 = [r[2] for r in rows]
print(f"n subjects: {len(rows)}")
print(f"onset>=21s: min={min(c21)} p10={sorted(c21)[11]} median={st.median(c21)} max={max(c21)}  n<20: {sum(1 for x in c21 if x < 20)}")
print(f"onset>=36s: min={min(c36)} p10={sorted(c36)[11]} median={st.median(c36)} max={max(c36)}  n<20: {sum(1 for x in c36 if x < 20)}")
print("subjects with n36 < 20:")
for sub, a, b in rows:
    if b < 20:
        print(f"  {sub}: frozen21={a} steady36={b}")
print("subjects whose count changed by >2:")
for sub, a, b in rows:
    if abs(a - b) > 2:
        print(f"  {sub}: {a} -> {b}")
