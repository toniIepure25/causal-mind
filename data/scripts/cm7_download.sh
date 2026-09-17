#!/bin/bash
# CM-7 minimal behavioral acquisition for OpenNeuro ds005494 (no iEEG).
# Robust: a 404 on any single file warns but does not abort.
BASE="https://s3.amazonaws.com/openneuro.org/ds005494"
DEST="/home/jovyan/work/causal-mind-v2/data/raw/ds005494"
mkdir -p "$DEST"

fetch() {
  # fetch <url> <dest>
  if curl -s -f -o "$2" "$1"; then
    echo "OK   $2"
  else
    echo "MISS $2  (url=$1)"
  fi
}

fetch "$BASE/participants.tsv" "$DEST/participants.tsv"
fetch "$BASE/dataset_description.json" "$DEST/dataset_description.json"
fetch "$BASE/stimuli/wordpools/wordpool_EN.txt" "$DEST/wordpool_EN.txt"

declare -A SESS
SESS[R1003P]="0 1"
SESS[R1016M]="0 1 2"
SESS[R1028M]="0"
SESS[R1031M]="0 1"
SESS[R1036M]="0"
SESS[R1050M]="0"
SESS[R1060M]="0 1"
SESS[R1074M]="0"
SESS[R1082N]="0"
SESS[R1091N]="1"
SESS[R1095N]="0"
SESS[R1111M]="0 1"
SESS[R1112M]="0"
SESS[R1118N]="0"
SESS[R1121M]="0"
SESS[R1130M]="0"
SESS[R1136N]="0"
SESS[R1149N]="0"
SESS[R1162N]="0"
SESS[R1185N]="0"

for SUB in "${!SESS[@]}"; do
  for SES in ${SESS[$SUB]}; do
    D="$DEST/sub-${SUB}/ses-${SES}"
    mkdir -p "$D"
    fetch "$BASE/sub-${SUB}/ses-${SES}/beh/sub-${SUB}_ses-${SES}_task-PAL2_beh.tsv" "$D/beh.tsv"
    fetch "$BASE/sub-${SUB}/ses-${SES}/ieeg/sub-${SUB}_ses-${SES}_task-PAL2_space-MNI152NLin6ASym_electrodes.tsv" "$D/electrodes.tsv"
    fetch "$BASE/sub-${SUB}/ses-${SES}/ieeg/sub-${SUB}_ses-${SES}_task-PAL2_acq-monopolar_channels.tsv" "$D/channels_monopolar.tsv"
    fetch "$BASE/sub-${SUB}/ses-${SES}/ieeg/sub-${SUB}_ses-${SES}_task-PAL2_acq-bipolar_channels.tsv" "$D/channels_bipolar.tsv"
  done
done

echo "=== SUMMARY ==="
echo "beh.tsv present: $(find "$DEST" -name beh.tsv | wc -l) / 26"
echo "total size: $(du -sh "$DEST" | cut -f1)"
echo "=== beh.tsv sizes (bytes) ==="
find "$DEST" -name beh.tsv -printf '%s %p\n' | sort -n
echo "=== DONE ==="
