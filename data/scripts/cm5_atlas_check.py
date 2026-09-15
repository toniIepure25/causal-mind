#!/usr/bin/env python3
import numpy as np
import nibabel as nib

base = "/home/jovyan/work/causal-mind-v2/data/atlases/nilearn_cache/schaefer_2018/"
img = nib.load(base + "Schaefer2018_400Parcels_7Networks_order_FSLMNI152_2mm.nii.gz")
arr = img.get_fdata()
print("shape", arr.shape, "dtype", img.get_data_dtype())
vals = np.unique(arr)
print("n unique:", len(vals), "min", vals.min(), "max", vals.max())
print("affine:\n", img.affine)
# parcel id histogram sanity
ids = vals[vals > 0]
print("n parcels:", len(ids), "first", ids[:5], "last", ids[-5:])
# read the order txt
txt = open(base + "Schaefer2018_400Parcels_7Networks_order.txt").read().splitlines()
print("order txt lines:", len(txt))
for line in txt[:12]:
    print("  ", line)
