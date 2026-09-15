#!/usr/bin/env python3
"""Summarize the pre-QC eligibility audit (read-only)."""
import csv
import statistics as st
from collections import Counter

rows = list(csv.DictReader(open("/home/jovyan/work/causal-mind-v2/reports/cm5_subject_eligibility.tsv"), delimiter="\t"))
safe = sorted(int(r["hrf_safe_target_count"]) for r in rows)
print("hrf_safe targets: min=%d p10=%d median=%d mean=%.1f max=%d"
      % (safe[0], safe[11], safe[59], st.mean(safe), safe[-1]))
print("n with <20:", sum(1 for x in safe if x < 20), " n with <30:", sum(1 for x in safe if x < 30))
bold = [int(r["bold_size"]) for r in rows if r["bold_available"] == "1"]
print("bold: n=%d total_GB=%.1f min_MB=%.0f max_MB=%.0f"
      % (len(bold), sum(bold) / 1e9, min(bold) / 1e6, max(bold) / 1e6))
conf = [int(r["confounds_size"]) for r in rows if r["confounds_available"] == "1"]
print("confounds: n=%d total_MB=%.0f" % (len(conf), sum(conf) / 1e6))
mask = [int(r["mask_size"]) for r in rows if r["mask_available"] == "1"]
print("masks: n=%d total_KB=%.0f" % (len(mask), sum(mask) / 1e3))
pend = [r for r in rows if r["eligibility_status"] == "PENDING_QC"]
print("split (pending):", dict(Counter(r["cm3_split"] for r in pend)))
print("excluded:", [(r["subject_id"], r["cm3_split"], r["exclusion_reason"])
                   for r in rows if r["eligibility_status"] != "PENDING_QC"])
# per-split pending counts
for part in ("train", "val", "test"):
    n = sum(1 for r in pend if r["cm3_split"] == part)
    print(f"  {part}: {n}")
