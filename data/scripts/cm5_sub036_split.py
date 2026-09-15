#!/usr/bin/env python3
import json
d = json.load(open("/home/jovyan/work/causal-mind-v2/reports/cm5_cohort_seal.json"))
for p in ("train", "val", "test"):
    if "sub-036" in d["included_subjects"][p]:
        print("sub-036 is in:", p)
# also confirm the 5 pre-scan subjects' splits (they are kept)
for s in ("sub-018", "sub-083", "sub-114", "sub-009", "sub-086"):
    for p in ("train", "val", "test"):
        if s in d["included_subjects"][p]:
            print(f"{s} in {p} (KEPT - aligned, pre-scan speech)")
