#!/usr/bin/env python3
import pandas as pd
q = pd.read_csv("/home/jovyan/work/causal-mind-v2/reports/cm5_qc_audit.tsv", sep="\t")
c = q[q["qc_status"] == "COMPUTED"]
print("dvars_gt50med_frac: min=%.3f p25=%.3f median=%.3f p75=%.3f max=%.3f" % (
    c["dvars_gt50med_frac"].min(), c["dvars_gt50med_frac"].quantile(0.25),
    c["dvars_gt50med_frac"].median(), c["dvars_gt50med_frac"].quantile(0.75),
    c["dvars_gt50med_frac"].max()))
hi = c[c["dvars_gt50med_frac"] > 0.5]
print("n with >50%% volumes DVARS>0.5*median:", len(hi))
print(list(zip(hi["subject_id"], hi["dvars_gt50med_frac"])))
print("std_dvars_mean: min=%.3f median=%.3f max=%.3f" % (
    c["std_dvars_mean"].min(), c["std_dvars_mean"].median(), c["std_dvars_mean"].max()))
exc = c[(c["fd_mean"] > 1.0) | (c["fd_gt10_frac"] > 0.5) | (c["fd_gt20_frac"] > 0.25)]
print("proposed motion exclusions:", list(zip(exc["subject_id"], exc["fd_mean"], exc["fd_gt10_frac"])))
