#!/usr/bin/env python3
import pandas as pd
import numpy as np

GIT = "/home/jovyan/work/ds006067_git"
DER = "/home/jovyan/work/causal-mind-v2/data/derived/thought_events"
sub = "sub-001"

# 1) raw MRI events
raw = pd.read_csv(f"{GIT}/{sub}/func/{sub}_task-thinkaloud_events.tsv", sep="\t")
print("=== raw events.tsv (MRI timebase) ===")
print("cols:", list(raw.columns))
print("n rows:", len(raw))
print(raw.head(3).to_string())
print("onset range:", raw["onset"].min(), raw["onset"].max())

# 2) OSF thought events
osf = pd.read_csv(f"{DER}/{sub}_thoughts.tsv", sep="\t")
print("\n=== OSF thought_events (derived) ===")
print("cols:", list(osf.columns))
print("n rows:", len(osf))
print(osf.head(3).to_string())
if "start_time" in osf.columns:
    print("start_time range:", osf["start_time"].min(), osf["start_time"].max())

# 3) compare counts + first transcripts
print("\n=== alignment check ===")
print("raw n:", len(raw), "osf n:", len(osf))
if "transcript" in raw.columns and "text" in osf.columns:
    print("raw[0] transcript:", repr(raw["transcript"].iloc[0][:60]))
    print("osf[0] text       :", repr(osf["text"].iloc[0][:60]))
    # do onsets match?
    if "start_time" in osf.columns:
        d = (raw["onset"].to_numpy() - osf["start_time"].to_numpy())
        print("onset - start_time: min %.3f max %.3f mean %.3f" % (d.min(), d.max(), d.mean()))
