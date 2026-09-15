#!/usr/bin/env python3
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "/home/jovyan/work/causal-mind-v2/src")
from causal_mind.data import osf_a56rm

GIT = "/home/jovyan/work/ds006067_git"
df = pd.read_csv("/home/jovyan/work/causal-mind-v2/reports/cm5_alignment_audit.tsv", sep="\t")
oor = df[df["in_range"] == 0]
print("OUT-OF-RANGE subjects:")
print(oor.to_string(index=False))
print()
for sub in list(oor["subject"]) + ["sub-036"]:
    raw = pd.read_csv(f"{GIT}/{sub}/func/{sub}_task-thinkaloud_events.tsv", sep="\t")
    osf = osf_a56rm.load_thought_events(sub)
    osf_starts = [e["onset"] for e in osf]
    print(f"=== {sub} ===")
    print(f"  raw: n={len(raw)} onset range [{raw['onset'].min():.1f}, {raw['onset'].max():.1f}]")
    print(f"  osf: n={len(osf)} start range [{min(osf_starts):.1f}, {max(osf_starts):.1f}]")
    print(f"  raw first 3 onsets: {list(raw['onset'].head(3))}")
    print(f"  osf first 3 starts: {[round(s,2) for s in osf_starts[:3]]}")
