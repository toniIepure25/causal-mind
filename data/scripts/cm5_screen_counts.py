#!/usr/bin/env python3
"""Count exclusions under candidate motion screens (for protocol documentation)."""
import pandas as pd

q = pd.read_csv("/home/jovyan/work/causal-mind-v2/reports/cm5_qc_audit.tsv", sep="\t")
c = q[q["qc_status"] == "COMPUTED"]
n = len(c)
strict_fd = c["fd_mean"] > 0.3
strict_frac = c["fd_gt05_frac"] > 0.10
strict = strict_fd | strict_frac
print(f"n with confounds: {n}")
print(f"strict (meanFD>0.3 OR >10% vol FD>0.5): {int(strict.sum())}/{n} = {strict.mean():.1%}")
print(f"  of which meanFD>0.3: {int(strict_fd.sum())}, >10%FD>0.5: {int(strict_frac.sum())}")
mod = c["fd_mean"] > 1.0
print(f"proposed (meanFD>1.0): {int(mod.sum())}/{n}")
topdec = c["fd_mean"] > c["fd_mean"].quantile(0.9)
print(f"top decile meanFD (>={c['fd_mean'].quantile(0.9):.3f}): {int(topdec.sum())} subjects: {list(topdec['subject_id'])}")
# split of strict-excluded
print("strict-excluded by split:", c[strict]["cm3_split"].value_counts().to_dict())
