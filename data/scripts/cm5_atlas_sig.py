#!/usr/bin/env python3
import inspect
from nilearn import datasets
print(inspect.signature(datasets.fetch_atlas_schaefer_2018))
print(datasets.fetch_atlas_schaefer_2018.__doc__[:1500])
