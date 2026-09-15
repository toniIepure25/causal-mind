#!/usr/bin/env python3
import re
lines = open("/home/jovyan/work/causal-mind-v2/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order.txt").read().splitlines()
names = [l.split("\t")[1] for l in lines]
print("sample raw names:")
for n in names[:3]:
    print(repr(n))
_NET_RE = re.compile(r"7Networks_(?:LH|RH)_(\w+)")
for n in names[:3]:
    m = _NET_RE.match(n)
    print("match:", m.group(1) if m else None)
# check: maybe split gives different
print("field0:", repr(lines[0].split("\t")[0]))
print("field1:", repr(lines[0].split("\t")[1]))
