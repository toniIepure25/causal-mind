#!/bin/bash
# Find the Schaefer 2018 400P FSLMNI152 2mm atlas files.
set -e
cd /home/jovyan/work/causal-mind-v2/data/atlases
echo "--- redirect chain for osf.io/865t3/download ---"
curl -sI -L https://osf.io/865t3/download 2>&1 | grep -iE "^location|^HTTP|content-length" | head -12
echo "--- try known nilearn mirror ---"
curl -sI https://osf.io/23y5u/download 2>&1 | grep -iE "^HTTP" | head -3
