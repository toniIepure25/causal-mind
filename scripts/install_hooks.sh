#!/usr/bin/env bash
# Install the Causal Mind git hooks (CM-REPO S43).
#
# Points core.hooksPath at scripts/hooks so the version-controlled hooks
# (pre-commit: human-data guard + lint ratchet) are used by this clone.
# Run once per clone:  scripts/install_hooks.sh
#
# NFS-safe: uses a temporary GIT_CONFIG_GLOBAL with safe.directory=* so the
# "dubious ownership" check (repo owned by a different uid on NFS) does not
# block writing the local repo config.
set -euo pipefail

# Temp global config so git accepts the NFS-owned repo (does not touch the
# user's real ~/.gitconfig).
_GIT_GLOBAL="$(mktemp)"
printf '[safe]\n\tdirectory = *\n' > "$_GIT_GLOBAL"
export GIT_CONFIG_GLOBAL="$_GIT_GLOBAL"
trap 'rm -f "$_GIT_GLOBAL"' EXIT

cd "$(git rev-parse --show-toplevel)"
chmod +x scripts/hooks/pre-commit
git config core.hooksPath scripts/hooks
echo "Installed git hooks (core.hooksPath=scripts/hooks)."
echo "  pre-commit: human-data guard + lint/type ratchet"
