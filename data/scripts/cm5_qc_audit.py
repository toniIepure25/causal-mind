#!/usr/bin/env python3
"""CM-5 cheap QC audit from fMRIPrep confounds TSVs (imaging QC only).

NO neural prediction outcomes are touched. Computes per-subject motion /
volume metrics from the confounds regressors:
  - n_volumes (row count; expected 400)
  - framewise displacement: mean/median/p95, proportion > 0.5/1.0/2.0 mm
    (first N_NONSTEADY volumes excluded from FD stats, fMRIPrep convention)
  - DVARS: mean, proportion of volumes with dvars > 1.5*median(dvars)
    (fMRIPrep/Power+2018 scrubber convention), excluding non-steady-state
  - missing/non-finite confound values in the core regressor set
Output: reports/cm5_qc_audit.tsv
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("/home/jovyan/work/causal-mind-v2")
NEURAL = ROOT / "data" / "neural" / "derivatives"
AUDIT = ROOT / "reports" / "cm5_subject_eligibility.tsv"
OUT = ROOT / "reports" / "cm5_qc_audit.tsv"

N_NONSTEADY = 10  # frozen: fMRIPrep non-steady-state convention
CORE_COLS = [
    "framewise_displacement", "dvars", "std_dvars", "global_signal",
    "csf", "white_matter", "tcompcor", "rmsd",
]


def main() -> int:
    elig = pd.read_csv(AUDIT, sep="\t")
    rows = []
    for _, r in elig.iterrows():
        sub = r["subject_id"]
        f = NEURAL / sub / "func" / f"{sub}_task-thinkaloud_desc-confounds_timeseries.tsv"
        row = {"subject_id": sub, "cm3_split": r["cm3_split"]}
        if not f.exists():
            row.update({c: np.nan for c in [
                "n_volumes", "fd_mean", "fd_median", "fd_p95",
                "fd_gt05_frac", "fd_gt10_frac", "fd_gt20_frac",
                "dvars_mean", "std_dvars_gt50med_frac", "n_missing_core",
                "n_nonfinite_core", "qc_status"]})
            row["qc_status"] = "NO_CONFOUNDS"
            rows.append(row)
            continue
        df = pd.read_csv(f, sep="\t")
        n_vol = len(df)
        fd = pd.to_numeric(df["framewise_displacement"], errors="coerce").iloc[N_NONSTEADY:]
        # fMRIPrep/Power+2018 scrubber: volumes with DVARS > 50% ABOVE the
        # median DVARS, i.e. dvars > 1.5 * median(dvars).
        dvars = pd.to_numeric(df["dvars"], errors="coerce").iloc[N_NONSTEADY:]
        std_dvars = pd.to_numeric(df["std_dvars"], errors="coerce").iloc[N_NONSTEADY:]
        med = dvars.median()
        # Missing/non-finite counted after the non-steady-state period
        # (fMRIPrep writes 'n/a' for FD/dvars on the first volume by design).
        core = df[CORE_COLS].apply(pd.to_numeric, errors="coerce").iloc[N_NONSTEADY:]
        n_missing = int(core.isna().sum().sum())
        n_nonfinite = int(np.isinf(core.to_numpy(dtype=float)).sum())
        row.update({
            "n_volumes": n_vol,
            "fd_mean": round(float(fd.mean()), 4),
            "fd_median": round(float(fd.median()), 4),
            "fd_p95": round(float(fd.quantile(0.95)), 4),
            "fd_gt05_frac": round(float((fd > 0.5).mean()), 4),
            "fd_gt10_frac": round(float((fd > 1.0).mean()), 4),
            "fd_gt20_frac": round(float((fd > 2.0).mean()), 4),
            "dvars_mean": round(float(dvars.mean()), 2),
            "dvars_gt50med_frac": round(float((dvars > 1.5 * med).mean()), 4),
            "std_dvars_mean": round(float(std_dvars.mean()), 4),
            "n_missing_core": n_missing,
            "n_nonfinite_core": n_nonfinite,
            "qc_status": "COMPUTED",
        })
        rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, sep="\t", index=False)
    print(f"wrote {OUT} ({len(out)} subjects)")
    comp = out[out["qc_status"] == "COMPUTED"]
    print("FD mean:  min=%.3f p25=%.3f median=%.3f p75=%.3f max=%.3f" % (
        comp["fd_mean"].min(), comp["fd_mean"].quantile(0.25),
        comp["fd_mean"].median(), comp["fd_mean"].quantile(0.75), comp["fd_mean"].max()))
    print("FD p95:   min=%.3f median=%.3f max=%.3f" % (
        comp["fd_p95"].min(), comp["fd_p95"].median(), comp["fd_p95"].max()))
    print("FD>0.5:   min=%.3f median=%.3f max=%.3f" % (
        comp["fd_gt05_frac"].min(), comp["fd_gt05_frac"].median(), comp["fd_gt05_frac"].max()))
    print("FD>1.0:   min=%.3f median=%.3f max=%.3f" % (
        comp["fd_gt10_frac"].min(), comp["fd_gt10_frac"].median(), comp["fd_gt10_frac"].max()))
    print("FD>2.0:   min=%.3f median=%.3f max=%.3f" % (
        comp["fd_gt20_frac"].min(), comp["fd_gt20_frac"].median(), comp["fd_gt20_frac"].max()))
    print("n_volumes: min=%d max=%d  (n!=400: %d)" % (
        comp["n_volumes"].min(), comp["n_volumes"].max(),
        int((comp["n_volumes"] != 400).sum())))
    print("missing core: max=%d  nonfinite: max=%d" % (
        comp["n_missing_core"].max(), comp["n_nonfinite_core"].max()))
    for c in ("fd_mean", "fd_gt05_frac", "fd_gt10_frac"):
        hi = comp[comp[c] > comp[c].quantile(0.9)]
        if len(hi):
            print(f"top-decile {c}: " + ", ".join(f"{s}={v}" for s, v in zip(hi["subject_id"], hi[c])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
