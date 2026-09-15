#!/usr/bin/env python3
"""Write the F2 (tSNR) post-acquisition gate sealed amendment.

The F2 gate (pre-registered in configs/cm5_eligibility.json) excludes subjects
with tSNR < 2.0 OR below the 5th percentile of the acquired cohort's tSNR
distribution. This is applied AFTER BOLD download, BEFORE any decisive neural
analysis, and documented here as a sealed amendment (it can only REMOVE
subjects, on pre-registered data-quality grounds).
"""
import hashlib
import json
import pandas as pd

ROOT = "/home/jovyan/work/causal-mind-v2"
seal = json.load(open(f"{ROOT}/reports/cm5_cohort_seal.json"))
man = pd.read_csv(f"{ROOT}/reports/cm5_feature_manifest.tsv", sep="\t").set_index("subject")
split = {}
for p in ("train", "val", "test"):
    for s in seal["included_subjects"][p]:
        split[s] = p

cohort = [s for s in seal["included_subjects"]["train"]
          + seal["included_subjects"]["val"] + seal["included_subjects"]["test"]]
tsnr = {s: float(man.loc[s, "tsnr"]) for s in cohort if s in man.index}
vals = sorted(tsnr.values())
p5 = vals[max(0, int(0.05 * len(vals)) - 1)] if len(vals) > 1 else vals[0]
# use pandas quantile for consistency with the analysis
tser = pd.Series(tsnr)
floor_pct = float(tser.quantile(0.05))
floor = max(2.0, floor_pct)
excl = sorted([s for s, v in tsnr.items() if v < floor])

post = {p: [s for s in seal["included_subjects"][p] if s not in excl]
        for p in ("train", "val", "test")}

amend = {
    "amendment_id": "CM5-F2-TSNR-1",
    "parent_seal": "CM5_ELIGIBILITY_SEAL",
    "gate": "F2_tsnr",
    "rule": "exclude if tSNR < 2.0 OR tSNR < cohort 5th percentile",
    "applied": "after BOLD download, before any decisive neural analysis",
    "can_add_subjects": False,
    "outcome_independent": True,
    "tsnr_distribution": {
        "min": float(tser.min()), "p5": floor_pct, "median": float(tser.median()),
        "max": float(tser.max()), "n": int(len(tser)),
    },
    "floor_applied": floor,
    "excluded": [{"subject": s, "split": split[s], "tsnr": tsnr[s]} for s in excl],
    "post_gate_split": post,
    "post_gate_n": sum(len(v) for v in post.values()),
    "hashes": {
        "feature_manifest": hashlib.sha256(
            open(f"{ROOT}/reports/cm5_feature_manifest.tsv", "rb").read()).hexdigest(),
        "parent_cohort_seal": hashlib.sha256(
            open(f"{ROOT}/reports/cm5_cohort_seal.json", "rb").read()).hexdigest(),
    },
}
out = f"{ROOT}/reports/cm5_cohort_amendment_f2_tsnr.json"
json.dump(amend, open(out, "w"), indent=2)
print(json.dumps(amend["post_gate_split"], indent=2))
print("excluded:", [(s, tsnr[s]) for s in excl])
print("post-gate n:", amend["post_gate_n"])
print("amendment sha256:", hashlib.sha256(open(out, "rb").read()).hexdigest())
print("wrote", out)
