#!/usr/bin/env bash
# bootstrap_environment.sh — reconstruct the CAUSAL MIND research environment from source.
#
# Goal: fresh pod -> clone -> bootstrap -> test -> reproduce, with no undocumented
# manual dependency installation. This is the fix for the pod-recreation weakness
# (the ephemeral rootfs destroyed the previous uv Python environment).
#
# Usage:
#   bash scripts/bootstrap_environment.sh            # core + dev deps
#   bash scripts/bootstrap_environment.sh --gpu      # + GPU (torch cu128)
#   bash scripts/bootstrap_environment.sh --test     # run the test suite after sync
#
# No secrets, no datasets. Deterministic dependency resolution via uv.lock.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

GPU=0
RUN_TESTS=0
NEURAL=1
for arg in "$@"; do
  case "$arg" in
    --gpu) GPU=1 ;;
    --test) RUN_TESTS=1 ;;
    --no-neural) NEURAL=0 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

# 1. Ensure uv is available (install to ~/.local/bin if missing).
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "[bootstrap] uv not found; installing..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi
echo "[bootstrap] uv $(uv --version)"

# 2. Pin the Python version. uv.lock was generated for the project's requires-python.
#    Prefer a CPython 3.11 interpreter (matches the frozen forecaster environment).
PYVER="${UV_PYTHON:-3.11}"
if ! uv python find "$PYVER" >/dev/null 2>&1; then
  echo "[bootstrap] installing CPython $PYVER via uv..."
  uv python install "$PYVER"
fi
echo "[bootstrap] using $(uv python find "$PYVER")"

# 3. Deterministic sync from uv.lock.
#    Default: core + dev + neural (sentence-transformers + nilearn + torch) so the full
#    scientific environment (MiniLM encoder, fMRI analysis, forecaster) is reproducible.
#    --no-neural gives a lightweight CPU environment (no torch) for CI-style checks.
if [ "$NEURAL" -eq 1 ]; then
  echo "[bootstrap] uv sync (core + dev + neural)..."
  uv sync --extra neural
else
  echo "[bootstrap] uv sync (core + dev, no neural)..."
  uv sync
fi

# 4. Optional GPU extra (pin torch to the cu128 build).
if [ "$GPU" -eq 1 ]; then
  echo "[bootstrap] uv sync --extra gpu (torch cu128)..."
  uv sync --extra gpu
fi

# 5. Report the environment.
echo "[bootstrap] python: $(.venv/bin/python --version)"
.venv/bin/python - <<'PY'
import importlib
mods = ["numpy", "pandas", "scipy", "sklearn", "pydantic", "yaml", "requests", "psutil"]
for m in mods:
    try:
        mod = importlib.import_module(m)
        print(f"  {m}: {getattr(mod, '__version__', 'ok')}")
    except Exception as e:
        print(f"  {m}: MISSING ({e})")
try:
    import torch
    print(f"  torch: {torch.__version__} (cuda={torch.cuda.is_available()})")
except Exception:
    print("  torch: not installed (CPU mode)")
PY

# 6. Optional test run.
if [ "$RUN_TESTS" -eq 1 ]; then
  echo "[bootstrap] running test suite..."
  .venv/bin/python -m pytest
fi

echo "[bootstrap] DONE"
