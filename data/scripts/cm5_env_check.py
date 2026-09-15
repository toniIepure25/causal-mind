#!/usr/bin/env python3
import importlib
for m in ("nibabel", "sklearn", "pandas", "numpy", "nilearn", "torch"):
    try:
        mod = importlib.import_module(m)
        print(m, getattr(mod, "__version__", "?"))
    except Exception as e:
        print(m, "MISSING", type(e).__name__)
