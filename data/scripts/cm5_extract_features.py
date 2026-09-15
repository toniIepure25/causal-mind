#!/usr/bin/env python3
"""Stage A (production): per-subject CM-5 feature extraction for the sealed cohort.

For each eligible subject:
  - load BOLD + mask, F1 gate (shape/TR/finite/affine/mask)
  - F2: tSNR (steady-state, mask)
  - resample Schaefer-400 atlas to the BOLD grid (done once, cached)
  - N1 (7 Yeo networks) + N2 (400 parcels) time series
  - selected fMRIPrep confounds (37 cols, frozen nuisance set)
  - raw MRI events (onset/duration/n_words) for speech-derived nuisance
Saves data/derived/cm5_features/{sub}.npz and reports/cm5_feature_manifest.tsv.
"""
from __future__ import annotations
import json
import re
import sys
import time
import numpy as np
import nibabel as nib
import pandas as pd

ROOT = "/home/jovyan/work/causal-mind-v2"
NEURAL = f"{ROOT}/data/neural/derivatives"
GIT = "/home/jovyan/work/ds006067_git"
ATLAS = f"{ROOT}/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz"
ORDER = f"{ROOT}/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order.txt"
FEAT = f"{ROOT}/data/derived/cm5_features"
MANIFEST = f"{ROOT}/reports/cm5_feature_manifest.tsv"
SEAL = f"{ROOT}/reports/cm5_cohort_seal.json"
MNI = "space-MNI152NLin2009cAsym"
TR = 1.5
N_VOL = 400
N_NONSTEADY = 10

NET_TOKEN = {
    "Vis": "visual", "SomMot": "somatomotor", "DorsAttn": "dorsal_attention",
    "SalVentAttn": "salience", "Limbic": "limbic",
    "Cont": "frontoparietal", "Default": "default_mode",
}
CONF_COLS = (["framewise_displacement", "dvars", "std_dvars", "rmsd",
              "global_signal", "csf", "white_matter"]
             + [f"t_comp_cor_{i:02d}" for i in range(10)]
             + [f"c_comp_cor_{i:02d}" for i in range(20)])


def load_order_names():
    return [l.split("\t")[1] for l in open(ORDER).read().splitlines()]


def network_of(parcel_id: int, order_names: list[str]) -> str:
    parts = order_names[parcel_id - 1].split("_")
    if len(parts) >= 3 and parts[2] in NET_TOKEN:
        return NET_TOKEN[parts[2]]
    return "unknown"


def resample_atlas_once(bold_shape_spatial, bold_aff):
    from nibabel.processing import resample_from_to
    a = nib.load(ATLAS)
    arr = a.get_fdata().astype(np.int32)
    ref = nib.Nifti1Image(np.zeros(bold_shape_spatial), bold_aff)
    res = resample_from_to(nib.Nifti1Image(arr.astype(np.float32), a.affine), ref, order=0)
    return res.get_fdata().astype(np.int32)


def main():
    import os
    os.makedirs(FEAT, exist_ok=True)
    seal = json.load(open(SEAL))
    subjects = (seal["included_subjects"]["train"]
                + seal["included_subjects"]["val"]
                + seal["included_subjects"]["test"])
    order_names = load_order_names()
    nets = list(NET_TOKEN.values())
    # parcel -> network
    net_of_parc = [network_of(p, order_names) for p in range(1, 401)]

    # All subjects share the same MNI152NLin2009cAsym grid; resample the atlas
    # once (using the first subject's affine) and assert every subject matches.
    first_img = nib.load(f"{NEURAL}/{subjects[0]}/func/{subjects[0]}_task-thinkaloud_{MNI}_desc-preproc_bold.nii.gz")
    ref_shape = first_img.shape[:3]
    ref_aff = first_img.affine
    labels = resample_atlas_once(ref_shape, ref_aff)
    print(f"atlas resampled once to {ref_shape}; affine diag {np.diag(ref_aff)[:3]}", flush=True)

    rows = []
    t0 = time.time()
    for si, sub in enumerate(subjects):
        t_s = time.time()
        bold_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_{MNI}_desc-preproc_bold.nii.gz"
        mask_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_{MNI}_desc-brain_mask.nii.gz"
        cf_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_desc-confounds_timeseries.tsv"
        ev_p = f"{GIT}/{sub}/func/{sub}_task-thinkaloud_events.tsv"
        f1 = "OK"
        # resumable: skip if already extracted
        if os.path.exists(f"{FEAT}/{sub}.npz"):
            z = np.load(f"{FEAT}/{sub}.npz")
            rows.append([sub, "OK", round(float(z["tsnr"]), 3), int(z["n_vox"]), 0])
            continue
        try:
            img = nib.load(bold_p)
            bold = np.ascontiguousarray(img.get_fdata(dtype=np.float32).transpose(3, 0, 1, 2))
            mask = nib.load(mask_p).get_fdata() > 0.5
            # F1 gate
            if bold.shape[0] != N_VOL:
                f1 = f"FAIL_nvol{bold.shape[0]}"
            if bold.shape[1:] != ref_shape or not np.allclose(img.affine, ref_aff):
                f1 = "FAIL_grid"
            if not np.isfinite(bold).all():
                f1 = "FAIL_nonfinite"
            if not mask.any():
                f1 = "FAIL_empty_mask"
            if f1 != "OK":
                rows.append([sub, f1, np.nan, 0, 0])
                continue
            ss = bold[N_NONSTEADY:]
            tsnr = float((ss.mean(axis=0) / (ss.std(axis=0) + 1e-8))[mask].mean())
            # N2
            vox_idx = np.argwhere(mask)
            lab_vox = labels[vox_idx[:, 0], vox_idx[:, 1], vox_idx[:, 2]]
            bold_vox = bold[:, vox_idx[:, 0], vox_idx[:, 1], vox_idx[:, 2]]
            n2 = np.zeros((N_VOL, 400), dtype=np.float32)
            for p in range(1, 401):
                idx = np.where(lab_vox == p)[0]
                if idx.size:
                    n2[:, p - 1] = bold_vox[:, idx].mean(axis=1)
            # N1
            n1 = np.zeros((N_VOL, len(nets)), dtype=np.float32)
            for i, net in enumerate(nets):
                ps = [p for p in range(400) if net_of_parc[p] == net]
                if ps:
                    n1[:, i] = n2[:, ps].mean(axis=1)
            # confounds (zero-pad missing CompCor columns; fMRIPrep fits a
            # variable number of components per subject)
            cf = pd.read_csv(cf_p, sep="\t")
            cfmat = np.zeros((len(cf), len(CONF_COLS)), dtype=np.float32)
            for j, c in enumerate(CONF_COLS):
                if c in cf.columns:
                    cfmat[:, j] = pd.to_numeric(cf[c], errors="coerce").fillna(0.0).to_numpy(dtype=np.float32)
            # raw events
            ev = pd.read_csv(ev_p, sep="\t")
            ev_onset = ev["onset"].to_numpy(dtype=np.float32)
            ev_dur = ev["duration"].to_numpy(dtype=np.float32)
            ev_nw = ev["transcript"].str.split().str.len().to_numpy(dtype=np.float32)
            np.savez_compressed(
                f"{FEAT}/{sub}.npz",
                n1=n1, n2=n2, conf=cfmat,
                ev_onset=ev_onset, ev_dur=ev_dur, ev_nw=ev_nw,
                tsnr=np.float32(tsnr), n_vox=np.int32(int(mask.sum())),
            )
            rows.append([sub, f1, round(tsnr, 3), int(mask.sum()), int(time.time() - t_s)])
            if si % 10 == 0:
                print(f"[{si}/{len(subjects)}] {sub} tSNR={tsnr:.2f} "
                      f"({time.time()-t_s:.1f}s) elapsed={time.time()-t0:.0f}s", flush=True)
        except Exception as e:
            rows.append([sub, f"ERROR:{type(e).__name__}", np.nan, 0, 0])
            print(f"  {sub} ERROR: {e}", flush=True)
    df = pd.DataFrame(rows, columns=["subject", "f1", "tsnr", "n_vox", "sec"])
    df.to_csv(MANIFEST, sep="\t", index=False)
    ok = df[df["f1"] == "OK"]
    print(f"\nDone {len(df)} subjects in {time.time()-t0:.0f}s")
    print(f"F1 OK: {len(ok)}, tSNR min={ok['tsnr'].min():.2f} median={ok['tsnr'].median():.2f} max={ok['tsnr'].max():.2f}")
    bad = df[df["f1"] != "OK"]
    if len(bad):
        print("F1 failures:")
        print(bad.to_string(index=False))
    print(f"wrote {MANIFEST}")


if __name__ == "__main__":
    main()
