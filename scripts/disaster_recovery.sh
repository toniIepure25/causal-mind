#!/usr/bin/env bash
# CM-LAB disaster-recovery test (S60/61).
#
# Proves the git repo is a COMPLETE, SELF-SUFFICIENT recovery source. It simulates
# total loss of the working environment (the pod-recreation weakness that destroyed the
# previous uv Python env) and rebuilds from the repo alone:
#
#     fresh clone  ->  bootstrap environment  ->  one-command validation  ->  frozen-artifact integrity
#
# The off-site (GitHub) backup is exercised by CI, which clones from GitHub on every push
# (the pod itself has no GitHub token, so this test clones from the local repo, which is
# the same content that is pushed to GitHub).
#
# Usage:
#   scripts/disaster_recovery.sh [source]     # default: the current repo
#
# Exits 0 only if every stage is green.
set -uo pipefail
# NFS ownership maps the repo to 'nobody'; make every git subprocess treat it as safe.
export GIT_CONFIG_COUNT=1
export GIT_CONFIG_KEY_0=safe.directory
export GIT_CONFIG_VALUE_0='*'
cd "$(dirname "$0")/.."
SRC="${1:-$(git rev-parse --show-toplevel)}"
WORK="$(mktemp -d /home/jovyan/work/dr_XXXXXX)"
echo "============================================================"
echo " CM-LAB disaster-recovery test"
echo " source: $SRC"
echo " work:   $WORK"
echo "============================================================"
trap 'rm -rf "$WORK"' EXIT

echo ""
echo "--- 1. fresh clone (repo is the only surviving artifact) ---"
git -c safe.directory=* clone --quiet "$SRC" "$WORK/repo" || { echo "DR: FAIL (clone)"; exit 1; }
cd "$WORK/repo"
echo "    HEAD: $(git -c safe.directory=* rev-parse --short HEAD)"

echo ""
echo "--- 2. bootstrap environment (core + dev + neural) ---"
bash scripts/bootstrap_environment.sh || { echo "DR: FAIL (bootstrap)"; exit 1; }

echo ""
echo "--- 3. one-command validation ---"
bash scripts/validate_project.sh || { echo "DR: FAIL (validate)"; exit 1; }

echo ""
echo "--- 4. frozen-artifact integrity (SHA registry) ---"
.venv/bin/python data/scripts/cm_lab_registry.py --check || { echo "DR: FAIL (integrity)"; exit 1; }

echo ""
echo "============================================================"
echo " DISASTER RECOVERY: PASS"
echo " (repo alone rebuilds a validated, scientifically-consistent environment)"
echo "============================================================"
