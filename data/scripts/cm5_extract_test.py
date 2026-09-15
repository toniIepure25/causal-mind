#!/usr/bin/env python3
"""Stage A: per-subject CM-5 feature extraction (test on one subject first).

For a subject: load BOLD + mask, validate (F1), tSNR (F2), resample the
Schaefer-400 atlas to the BOLD grid, compute N1 (7 Yeo networks) and N2
(400 parcels) time series, load confounds + speech-derived nuisance, and load
the frozen behavioral states (MiniLM). Saves a .npz per subject.
"""
from __future__ import annotations
import sys
import numpy as np
import nibabel as nib
import pandas as pd

ROOT = "/home/jovyan/work/causal-mind-v2"
NEURAL = f"{ROOT}/data/neural/derivatives"
GIT = "/home/jovyan/work/ds006067_git"
ATLAS = f"{ROOT}/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz"
MNI = "space-MNI152NLin2009cAsym"
TR = 1.5
N_VOL = 400

# Yeo 7-network grouping from the first token after 7Networks_<Hemi>_.
import re
NET_TOKEN = {
    "Vis": "visual", "SomMot": "somatomotor", "DorsAttn": "dorsal_attention",
    "SalVentAttn": "salience", "Limbic": "limbic",
    "Cont": "frontoparietal", "Default": "default_mode",
}
_NET_RE = re.compile(r"7Networks_(?:LH|RH)_(\w+?)_\d+$")


def load_atlas_parcels():
    img = nib.load(ATLAS)
    arr = img.get_fdata().astype(np.int32)
    return arr, img.affine


def resample_atlas_to_bold(atlas_arr, atlas_aff, spatial_shape, bold_aff):
    """Nearest-neighbor resample of the parcel label volume to the BOLD grid.

    ``spatial_shape`` is (x, y, z) of the BOLD (no time axis).
    """
    from nibabel.processing import resample_from_to
    atlas_img = nib.Nifti1Image(atlas_arr.astype(np.float32), atlas_aff)
    ref_img = nib.Nifti1Image(np.zeros(spatial_shape), bold_aff)
    res = resample_from_to(atlas_img, ref_img, order=0)  # 0 = nearest
    return res.get_fdata().astype(np.int32)


def network_of(parcel_id: int, order_names: list[str]) -> str:
    # name looks like 7Networks_<Hemi>_<Network>_<subregion>_<num>
    # The Yeo network is the 3rd underscore-delimited field.
    parts = order_names[parcel_id - 1].split("_")
    if len(parts) >= 3 and parts[2] in NET_TOKEN:
        return NET_TOKEN[parts[2]]
    return "unknown"


def main():
    sub = sys.argv[1] if len(sys.argv) > 1 else "sub-001"
    bold_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_{MNI}_desc-preproc_bold.nii.gz"
    mask_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_{MNI}_desc-brain_mask.nii.gz"
    cf_p = f"{NEURAL}/{sub}/func/{sub}_task-thinkaloud_desc-confounds_timeseries.tsv"

    img = nib.load(bold_p)
    bold = np.ascontiguousarray(img.get_fdata(dtype=np.float32).transpose(3, 0, 1, 2))  # (T, x, y, z)
    mask = nib.load(mask_p).get_fdata() > 0.5
    print(f"{sub}: bold {bold.shape} mask vox {int(mask.sum())}")

    # F1 gate
    assert bold.shape[0] == N_VOL, f"n_vol {bold.shape[0]} != {N_VOL}"
    assert np.isfinite(bold).all(), "non-finite BOLD"
    assert mask.any(), "empty mask"

    # tSNR (steady-state volumes 10..): mean over voxels of mean/std
    ss = bold[10:]
    tsnr_vox = ss.mean(axis=0) / (ss.std(axis=0) + 1e-8)
    tsnr = float(tsnr_vox[mask].mean())
    print(f"tSNR (steady-state, mask): {tsnr:.3f}")

    # atlas resample
    atlas_arr, atlas_aff = load_atlas_parcels()
    labels = resample_atlas_to_bold(atlas_arr, atlas_aff, bold.shape[1:], img.affine)
    print("resampled labels shape", labels.shape, "unique", len(np.unique(labels)))
    # parcel voxel counts within mask
    lab = labels[mask]
    uniq, counts = np.unique(lab, return_counts=True)
    print("parcels with voxels in mask:", int((uniq > 0).sum()), "min vox", int(counts[uniq > 0].min()))

    # order names for network grouping
    order = [l.split("\t")[1] for l in
             open(f"{ROOT}/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order.txt").read().splitlines()]

    # N2: 400 parcel time series
    vox_idx = np.argwhere(mask)
    lab_vox = labels[vox_idx[:, 0], vox_idx[:, 1], vox_idx[:, 2]]
    bold_vox = bold[:, vox_idx[:, 0], vox_idx[:, 1], vox_idx[:, 2]]  # (T, n_vox)
    n2 = np.zeros((N_VOL, 400), dtype=np.float32)
    for p in range(1, 401):
        sel = lab_vox == p
        if sel.any():
            n2[:, p - 1] = bold_vox[:, sel].mean(axis=1)
    print("N2 (T,400) done, std per parcel mean", float(n2.std(axis=0).mean()))

    # N1: 7 Yeo networks = mean of member parcels
    net_parcels: dict[str, list[int]] = {}
    for p in range(1, 401):
        net_parcels.setdefault(network_of(p, order), []).append(p - 1)
    nets = list(NET_TOKEN.values())
    n1 = np.zeros((N_VOL, len(nets)), dtype=np.float32)
    for i, net in enumerate(nets):
        ps = net_parcels.get(net, [])
        if ps:
            n1[:, i] = n2[:, ps].mean(axis=1)
    print("N1 (T,7) done; nets:", {k: len(v) for k, v in net_parcels.items()})

    # confounds
    cf = pd.read_csv(cf_p, sep="\t")
    print("confounds cols:", len(cf.columns), "rows", len(cf))
    print("OK", sub)


if __name__ == "__main__":
    main()
