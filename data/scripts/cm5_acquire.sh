#!/bin/bash
# CM-5 BOLD acquisition for the specified subjects (sub-001, sub-005 first).
#
# The fMRIPrep MNI derivatives are git-annexed in the OpenNeuro ds006067 clone at
# /home/jovyan/work/ds006067_git. Acquisition is currently blocked because the
# OpenNeuro dataset API (which mints S3 signed URLs) has no A record and the
# public S3 content bucket returns 403 for the annex keys. A retry poller
# (/home/jovyan/work/cm5_access_retry.sh) watches for the API to come back.
#
# This script fetches the needed files once access is available, then validates
# them. It tries, in order:
#   1. git-annex get from the OpenNeuro annex remote (works when the API is up)
#   2. a manually-provided S3 signed URL (OPENNEURO_SIGNED_URL_<sub> env vars)
#
# Usage: bash data/scripts/cm5_acquire.sh [sub-001 sub-005]
set -euo pipefail

GA=/home/jovyan/work/.local/git-annex/git-annex.linux/git-annex
REPO=/home/jovyan/work/ds006067_git
PROJ=/home/jovyan/work/causal-mind-v2
SUBS="${1:-sub-001 sub-005}"

cd "$REPO"
for sub in $SUBS; do
  echo "=== acquiring $sub ==="
  files=(
    "derivatives/$sub/func/${sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
    "derivatives/$sub/func/${sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.json"
    "derivatives/$sub/func/${sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz"
    "derivatives/$sub/func/${sub}_task-thinkaloud_desc-confounds_timeseries.tsv"
    "derivatives/$sub/func/${sub}_task-thinkaloud_desc-confounds_timeseries.json"
  )
  # 1) git-annex (works when the OpenNeuro API/annex server is reachable)
  "$GA" get --from=openneuro "${files[@]}" 2>&1 | head -4 \
    || echo "  git-annex get failed (OpenNeuro API likely still down)"
  # 2) manual signed URL fallback (if provided)
  url="${!OPENNEURO_SIGNED_URL_${sub//-/}_MNI:-}"
  if [ -n "${url:-}" ]; then
    curl -fsSL "$url" -o "${files[0]}" && echo "  fetched via signed URL"
  fi
  # validate
  "$PROJ/.venv/bin/python" "$PROJ/data/scripts/cm5_validate_bold.py" \
    --subject "$sub" \
    --derivatives "$REPO/derivatives" \
    --raw "$REPO" \
    && echo "  $sub VALIDATION PASS" || echo "  $sub VALIDATION FAILED"
done
