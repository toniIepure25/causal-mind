#!/usr/bin/env python3
import numpy as np
import nibabel as nib

img = nib.load("/home/jovyan/work/causal-mind-v2/data/neural/derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz")
print("BOLD shape", img.shape, "dtype", img.get_data_dtype())
print("BOLD affine:\n", img.affine)
mask = nib.load("/home/jovyan/work/causal-mind-v2/data/neural/derivatives/sub-001/func/sub-001_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz")
m = mask.get_fdata()
print("mask shape", m.shape, "n brain vox", int((m > 0.5).sum()))
print("mask affine:\n", mask.affine)
# atlas affine for comparison
at = nib.load("/home/jovyan/work/causal-mind-v2/data/atlases/nilearn_cache/schaefer_2018/Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz")
print("atlas affine:\n", at.affine, "shape", at.shape)
# voxel size difference
print("bold zooms", img.header.get_zooms())
print("atlas zooms", at.header.get_zooms())
