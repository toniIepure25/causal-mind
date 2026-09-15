#!/usr/bin/env python3
import json, pandas as pd
seal = json.load(open("/home/jovyan/work/causal-mind-v2/reports/cm5_cohort_seal.json"))
split = {}
for p in ("train", "val", "test"):
    for s in seal["included_subjects"][p]:
        split[s] = p
f2 = ["sub-012", "sub-017", "sub-019", "sub-032", "sub-047", "sub-083"]
from collections import Counter
print("F2 excluded split distribution:", Counter(split[s] for s in f2))
man = pd.read_csv("/home/jovyan/work/causal-mind-v2/reports/cm5_feature_manifest.tsv", sep="\t").set_index("subject")
for s in f2:
    print(f"  {s} ({split[s]}): tSNR={man.loc[s,'tsnr']}")
# post-F2 split sizes
from collections import defaultdict
sizes = Counter(split[s] for s in split if s not in f2)
print("post-F2 split sizes:", dict(sizes), "total", sum(sizes.values()))
