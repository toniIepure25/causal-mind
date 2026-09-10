#!/usr/bin/env bash
set -euo pipefail

export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=safe.directory GIT_CONFIG_VALUE_0=*

ROOT="${1:-/home/jovyan/work/worktrees/causal-mind-v2}"
REPO="$(git rev-parse --show-toplevel)"

mkdir -p "$ROOT"

create_worktree() {
    local name="$1"
    local branch="$2"
    local path="$ROOT/$name"
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        :
    else
        git branch "$branch" main
    fi
    if [ -d "$path/.git" ] || [ -f "$path/.git" ]; then
        echo "$name already exists at $path"
    else
        git -C "$REPO" worktree add "$path" "$branch"
    fi
}

create_worktree researcher agent/researcher
create_worktree data agent/data
create_worktree forecasting agent/forecasting
create_worktree causal agent/causal
create_worktree reviewer agent/reviewer
