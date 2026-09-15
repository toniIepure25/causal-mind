#!/usr/bin/env python3
import pandas as pd
cf = pd.read_csv("/home/jovyan/work/causal-mind-v2/data/neural/derivatives/sub-001/func/sub-001_task-thinkaloud_desc-confounds_timeseries.tsv", sep="\t")
cols = list(cf.columns)
print("n cols:", len(cols))
want = ["framewise_displacement", "dvars", "std_dvars", "rmsd", "global_signal", "csf", "white_matter"]
want += [f"t_comp_cor_{i:02d}" for i in range(10)]
want += [f"c_comp_cor_{i:02d}" for i in range(20)]
missing = [w for w in want if w not in cols]
present = [w for w in want if w in cols]
print("present:", len(present), "missing:", missing)
# how many c_comp_cor exist
cc = [c for c in cols if c.startswith("c_comp_cor")]
tc = [c for c in cols if c.startswith("t_comp_cor")]
print("n c_comp_cor:", len(cc), "n t_comp_cor:", len(tc))
print(cc)
