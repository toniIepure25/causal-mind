#!/usr/bin/env bash
# CM-LAB one-command project validation (S6).
#
# Usage:
#   scripts/validate_project.sh           # full validation (lint + tests + invariants + registries + linter + secret scan)
#   scripts/validate_project.sh --fast    # fast gate (no full test suite) for CI / pre-commit
#
# Exits 0 only if every check passes. Designed to be the single command a new
# collaborator (or CI) runs to confirm the project is healthy.
set -uo pipefail
cd "$(dirname "$0")/.."

FAST=0
[ "${1:-}" = "--fast" ] && FAST=1

# Locate the project python (uv venv first, then PATH).
PY=".venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3 || command -v python)"

echo "============================================================"
echo " CAUSAL MIND — one-command validation"
echo " python: $PY ($($PY --version 2>&1))"
echo " mode:   $([ "$FAST" = 1 ] && echo fast || echo full)"
echo "============================================================"

FAILURES=()
run() {
  local name="$1"; shift
  echo ""
  echo "--- $name ---"
  if "$@"; then
    echo "[PASS] $name"
  else
    echo "[FAIL] $name"
    FAILURES+=("$name")
  fi
}

# 1. Lint + type ratchet (fails only on NEW debt vs baseline; see cm_lab_lint_gate.py)
run "lint/type ratchet" "$PY" data/scripts/cm_lab_lint_gate.py

# 3. Test suite
if [ "$FAST" = 0 ]; then
  run "tests (pytest full)" "$PY" -m pytest tests/ -q
fi

# 4. Scientific invariants (always run)
run "invariants (pytest)" "$PY" -m pytest tests/test_invariants.py -q

# 5. Claims graph schema + traceability
run "claims graph (--check)" "$PY" data/scripts/cm_lab_claims_graph.py --check

# 6. Registry + frozen-artifact integrity
run "registry integrity (--check)" "$PY" data/scripts/cm_lab_registry.py --check

# 7. Claim linter (no overclaiming language)
run "claim linter" "$PY" data/scripts/cm_pub_claim_linter.py

# 8. Secret scan (conservative: long literals assigned to credential-looking names)
echo ""
echo "--- secret scan ---"
SECRET_HITS="$(grep -rInE "(api[_-]?key|secret|token|passwd|password|bearer)\s*[:=]\s*['\"][A-Za-z0-9+/=_-]{16,}['\"]" \
  --include='*.py' --include='*.sh' --include='*.json' --include='*.yaml' --include='*.yml' \
  src data/scripts scripts 2>/dev/null | grep -viE "example|placeholder|your_|<|dummy|changeme" || true)"
if [ -n "$SECRET_HITS" ]; then
  echo "$SECRET_HITS"
  echo "[FAIL] secret scan"
  FAILURES+=("secret scan")
else
  echo "[PASS] secret scan"
fi

echo ""
echo "============================================================"
if [ ${#FAILURES[@]} -eq 0 ]; then
  echo " VALIDATION: PASS (all checks green)"
  echo "============================================================"
  exit 0
else
  echo " VALIDATION: FAIL (${#FAILURES[@]} check(s)): ${FAILURES[*]}"
  echo "============================================================"
  exit 1
fi
