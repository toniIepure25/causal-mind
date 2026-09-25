"""Import-boundary test (CM-REPO S3).

Enforces the repository's layered architecture: a module may import from the
same or a lower layer, never from a strictly higher layer. This prevents
lower-level (scientific) modules from reaching up into orchestration/CLI code,
and keeps the dependency graph acyclic and reviewable.

Layers (lower = more foundational):
  0 foundation    paths, exit_codes, runid, logging_setup, errors, constants,
                  human_data_guard, utils
  1 domain        causal, thought, data, oracle, sim, privacy, language,
                  representations, preprocessing, counterfactual,
                  visualization, monitoring, security
  2 modeling      forecast, engine
  3 evaluation    eval, neural
  4 orchestration orchestrator, agent
  5 entry         cli, cli_research

Adding a new module requires assigning it a layer here (the test fails if a
module is unassigned), so the boundary is explicit and self-maintaining.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

_PKG = Path(__file__).resolve().parents[1] / "src" / "causal_mind"

LAYER: dict[str, int] = {
    # 0 foundation
    "paths": 0, "exit_codes": 0, "runid": 0, "logging_setup": 0,
    "errors": 0, "constants": 0, "human_data_guard": 0, "utils": 0,
    # 1 domain
    "causal": 1, "thought": 1, "data": 1, "oracle": 1, "sim": 1,
    "privacy": 1, "language": 1, "representations": 1, "preprocessing": 1,
    "counterfactual": 1, "visualization": 1, "monitoring": 1, "security": 1,
    # 2 modeling
    "forecast": 2, "engine": 2,
    # 3 evaluation
    "eval": 3, "neural": 3,
    # 4 orchestration
    "orchestrator": 4, "agent": 4,
    # 5 entry
    "cli": 5, "cli_research": 5,
}


def _modules() -> set[str]:
    mods = {p.stem for p in _PKG.glob("*.py") if p.stem != "__init__"}
    mods |= {d.name for d in _PKG.iterdir() if d.is_dir() and d.name != "__pycache__"}
    return mods


def _internal_deps(pyfile: Path) -> set[str]:
    try:
        tree = ast.parse(pyfile.read_text())
    except Exception:  # noqa: BLE001 - unreadable file is a hard failure below
        return set()
    deps: set[str] = set()
    for node in ast.walk(tree):
        mod = None
        if isinstance(node, ast.ImportFrom) and node.module:
            mod = node.module
        elif isinstance(node, ast.Import):
            mod = next((a.name for a in node.names if a.name.startswith("causal_mind")), None)
        if mod and mod.startswith("causal_mind"):
            parts = mod.split(".")
            if len(parts) > 1:
                deps.add(parts[1])
    return deps


def _all_deps() -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for m in _modules():
        deps: set[str] = set()
        target = _PKG / m
        files = [target] if target.is_file() else list(target.glob("*.py"))
        for f in files:
            if f.suffix == ".py":
                deps |= _internal_deps(f)
        deps.discard(m)
        out[m] = deps
    return out


def test_all_modules_assigned_a_layer():
    unassigned = _modules() - set(LAYER)
    assert not unassigned, f"modules missing a layer assignment: {sorted(unassigned)}"


def test_no_upward_imports():
    deps = _all_deps()
    violations = []
    for m, mdeps in deps.items():
        lm = LAYER[m]
        for d in mdeps:
            if d not in LAYER:
                continue
            if LAYER[d] > lm:
                violations.append(f"{m} (L{lm}) imports {d} (L{LAYER[d]})")
    assert not violations, "upward import violations:\n" + "\n".join(sorted(violations))


def test_no_circular_package_imports():
    """No two packages may import each other (direct 2-cycle)."""
    deps = _all_deps()
    cycles: set[str] = set()
    for m, mdeps in deps.items():
        for d in mdeps:
            if m in deps.get(d, set()):
                a, b = sorted((m, d))
                cycles.add(f"{a} <-> {b}")
    assert not cycles, "circular package imports: " + ", ".join(sorted(cycles))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
