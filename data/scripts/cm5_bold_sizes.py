#!/usr/bin/env python3
import csv
rows = list(csv.DictReader(open("/home/jovyan/work/causal-mind-v2/reports/cm5_subject_eligibility.tsv"), delimiter="\t"))
sizes = sorted((int(r["bold_size"]), r["subject_id"], r["bold_annex_key"]) for r in rows)
print("smallest 5 bold sizes:")
for s, sub, key in sizes[:5]:
    print(f"  {sub}: {s} bytes  key={key}")
print("largest 3:")
for s, sub, key in sizes[-3:]:
    print(f"  {sub}: {s} bytes  key={key}")
