#!/usr/bin/env python3
import re
lines = open("/home/jovyan/work/causal-mind-v2/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order.txt").read().splitlines()
names = [l.split("\t")[1] for l in lines]
# extract the network token: names look like 7Networks_LH_Vis_1
pats = {}
for n in names:
    # after 7Networks_<Hemi>_ comes the network token then _<num>
    m = re.match(r"7Networks_(LH|RH)_(.+?)_(\d+)$", n)
    if m:
        tok = m.group(2)
        pats.setdefault(tok, 0)
        pats[tok] += 1
    else:
        print("NOMATCH:", n)
for k, v in sorted(pats.items()):
    print(f"{k}: {v}")
print("total:", sum(pats.values()))
