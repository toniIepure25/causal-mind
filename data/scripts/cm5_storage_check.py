#!/usr/bin/env python3
"""Storage feasibility check for the sealed CM-5 cohort BOLD acquisition."""
import json
import pandas as pd
import subprocess

ROOT = "/home/jovyan/work/causal-mind-v2"
seal = json.load(open(f"{ROOT}/reports/cm5_cohort_seal.json"))
meta = pd.read_csv(f"{ROOT}/reports/cm5_subject_eligibility.tsv", sep="\t")
elig = meta[meta["final_eligible"] == 1]

bold_bytes = int(elig["bold_size"].sum())
conf_bytes = int(elig["confounds_size"].sum())
mask_bytes = int(elig["mask_size"].sum())
print(f"eligible subjects: {len(elig)}")
print(f"BOLD total:      {bold_bytes/1e9:.2f} GB")
print(f"confounds total: {conf_bytes/1e6:.1f} MB (already downloaded)")
print(f"masks total:     {mask_bytes/1e3:.1f} KB")
total = bold_bytes + mask_bytes
print(f"to download:     {total/1e9:.2f} GB")

out = subprocess.run(["df", "-B", "G", "/home/jovyan/work"],
                     capture_output=True, text=True).stdout
print("df /home/jovyan/work:")
print(out)
free_tb = None
for line in out.strip().splitlines()[1:]:
    parts = line.split()
    if len(parts) >= 4:
        free_tb = int(parts[3])
print(f"free (GB): {free_tb}")
if free_tb:
    print(f"download/available: {total/1e9:.2f} / {free_tb} GB "
          f"({(total/1e9)/free_tb:.3%})")
# feature cache estimate: 400 vols x 500 feats x 4B x 113 subj
feat = 400 * 500 * 4 * len(elig)
print(f"feature cache estimate (N1-N3, ~500 feats): {feat/1e6:.1f} MB")
# existing neural dir
import os
tot = 0
for dp, dn, fn in os.walk(f"{ROOT}/data/neural"):
    for f in fn:
        tot += os.path.getsize(os.path.join(dp, f))
print(f"existing data/neural: {tot/1e9:.2f} GB")
