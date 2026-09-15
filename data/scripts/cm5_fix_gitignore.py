#!/usr/bin/env python3
"""Fix .gitignore: replace the mangled last line with proper ignore rules."""
from pathlib import Path
p = Path("/home/jovyan/work/causal-mind-v2/.gitignore")
lines = p.read_text().splitlines()
# Drop the mangled garbage line (contains the concatenated patterns)
lines = [ln for ln in lines if "ndata/derived" not in ln and ln.strip() != ""]
# Ensure the three data-dir ignore rules are present (dedup)
for rule in ["data/neural/", "data/derived/cm5_features/", "data/atlases/"]:
    if rule not in lines:
        lines.append(rule)
p.write_text("\n".join(lines) + "\n")
print("fixed .gitignore; last 4 lines:")
print("\n".join(lines[-4:]))
