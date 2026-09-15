#!/usr/bin/env python3
"""Fetch Schaefer 2018 400P atlas (LR, 2mm, 7 Yeo networks) via nilearn."""
from nilearn import datasets
import nibabel as nib
import numpy as np

d = datasets.fetch_atlas_schaefer_2018(
    n_rois=400, yeo_networks=7, resolution_mm=2,
    data_dir="/home/jovyan/work/causal-mind-v2/data/atlases/nilearn_cache")
print("keys:", list(d.keys))
for k in d.keys:
    v = getattr(d, k)
    if isinstance(v, (list, tuple)) and v and hasattr(v[0], "shape"):
        print(k, "n_images", len(v), "shape", v[0].shape)
    else:
        print(k, "=", v if not isinstance(v, (list, tuple, np.ndarray)) else type(v))

parc = nib.load(d.images[0])
arr = parc.get_fdata()
print("parcellation shape", arr.shape, "n parcels", len(np.unique(arr)) - 1, "max", arr.max())
print("affine:\n", parc.affine)
out = "/home/jovyan/work/causal-mind-v2/data/atlases/schaefer2018_400p_7n_lr_mni2mm.nii.gz"
nib.save(nib.Nifti1Image(arr.astype(np.int16), parc.affine, parc.header), out)
print("saved parcellation ->", out)
# save the networks image too (Yeo 7 assignment per parcel/voxel)
if len(d.images) > 1:
    net = nib.load(d.images[1])
    nout = "/home/jovyan/work/causal-mind-v2/data/atlases/schaefer2018_400p_7n_labels_mni2mm.nii.gz"
    nib.save(nib.Nifti1Image(net.get_fdata().astype(np.int16), net.affine, net.header), nout)
    print("saved networks ->", nout, "unique", np.unique(net.get_fdata()))
