"""Research-facing CLI commands (CM-REPO S6/S18/S114).

Thin, well-structured entry points that REUSE the canonical checkers under
``data/scripts/`` (no reimplementation) and add the missing research surface
(``doctor``, ``demo``, ``reproduce``). Each handler returns an exit code from
:mod:`causal_mind.exit_codes`.

Commands
  doctor            environment / dependency / path / data diagnostics
  validate          run the scientific-integrity gates (reuse canonical checkers)
  claims verify     claim graph schema + traceability
  artifacts verify  registry + frozen-artifact SHA integrity
  security scan     security audit + secret scan + human-data guard
  demo              fast demo pipeline
  reproduce         run a named reproduction (cm8 | deep-dive | <script>)
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from causal_mind import constants, human_data_guard, paths
from causal_mind.exit_codes import ExitCode
from causal_mind.logging_setup import config_logging

# Keep interactive output clean; structured INFO logs only when CM_LOG_JSON=1.
_log = config_logging("cm.cli", level=logging.WARNING if os.environ.get("CM_LOG_JSON") != "1" else logging.INFO)


def _repo_root() -> Path:
    return paths.repo_root()


def _python() -> str:
    venv = _repo_root() / ".venv" / "bin" / "python"
    return str(venv) if venv.is_file() else sys.executable


def _run(name: str, argv: list[str], *, timeout: int = 1800) -> tuple[bool, int, str]:
    """Run a checker; return (ok, exit_code, tail). Never raises on non-zero."""
    _log.info("running check", extra={"check": name})
    try:
        proc = subprocess.run(
            argv, cwd=_repo_root(), capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        return False, int(ExitCode.GENERIC), f"{name}: TIMEOUT after {timeout}s"
    tail = "\n".join((proc.stdout or proc.stderr).splitlines()[-6:])
    return proc.returncode == 0, proc.returncode, tail


def _print_check(ok: bool, name: str, tail: str = "") -> None:
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}")
    if not ok and tail:
        for line in tail.splitlines():
            print(f"        {line}")


# --------------------------------------------------------------------------- #
# doctor
# --------------------------------------------------------------------------- #
def _cmd_doctor(args: argparse.Namespace) -> int:
    root = _repo_root()
    failures: list[str] = []

    def check(ok: bool, label: str, detail: str = "") -> None:
        print(f"[{'ok' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
        if not ok:
            failures.append(label)

    # 1. repo root
    check((root / "pyproject.toml").is_file(), "repo root discoverable", str(root))
    # 2. venv
    check((_repo_root() / ".venv" / "bin" / "python").is_file(), "uv venv present")
    # 3. key deps importable
    for mod in ("numpy", "pandas", "sklearn", "torch", "transformers"):
        try:
            __import__(mod)
            check(True, f"import {mod}")
        except Exception as exc:  # noqa: BLE001 - report any import failure
            check(False, f"import {mod}", f"{type(exc).__name__}: {exc}")
    # 4. frozen configs present + consistent
    try:
        c8, c2, c3 = constants.cm8(), constants.cm2(), constants.cm3()
        check(True, "frozen configs load", f"CM8 h*={c8.h_star} k={c8.k} horizons={c8.horizons}")
        check(c8.horizons == c3.event_horizons, "CM8.horizons == CM3.event_horizons")
        check(len(c2.train) == c8.n_train and len(c2.val) == c8.n_val and len(c2.test) == c8.n_test,
              "CM2 split sizes == CM8 split")
        check(c2.seed == c8.split_seed, "CM2 seed == CM8 split_seed")
    except Exception as exc:  # noqa: BLE001
        check(False, "frozen configs load", f"{type(exc).__name__}: {exc}")
    # 5. data dirs
    for d in ("data", "data/manifests", "data/derived/thought_events"):
        check((root / d).is_dir(), f"data dir {d}/")
    # 6. human data guard
    hits = human_data_guard.scan(root)
    check(not hits, "no human data staged", f"{len(hits)} hit(s)" if hits else "clean")

    print()
    if failures:
        print(f"DOCTOR: FAIL ({len(failures)} problem(s)): {', '.join(failures)}")
        return int(ExitCode.ENVIRONMENT)
    print("DOCTOR: OK (environment healthy)")
    return int(ExitCode.OK)


# --------------------------------------------------------------------------- #
# validate
# --------------------------------------------------------------------------- #
def _cmd_validate(args: argparse.Namespace) -> int:
    py = _python()
    root = _repo_root()
    results: list[tuple[str, bool, int]] = []

    def gate(name: str, argv: list[str], code: int) -> None:
        ok, rc, tail = _run(name, argv)
        _print_check(ok, name, tail)
        results.append((name, ok, code))

    gate("lint/type ratchet", [py, "data/scripts/cm_lab_lint_gate.py"], int(ExitCode.VALIDATION))
    gate("invariants", [py, "-m", "pytest", "tests/test_invariants.py", "-q"], int(ExitCode.PROTOCOL_VIOLATION))
    gate("claims graph", [py, "data/scripts/cm_lab_claims_graph.py", "--check"], int(ExitCode.VALIDATION))
    gate("registry integrity", [py, "data/scripts/cm_lab_registry.py", "--check"], int(ExitCode.ARTIFACT_MISMATCH))
    gate("claim linter", [py, "data/scripts/cm_pub_claim_linter.py"], int(ExitCode.VALIDATION))
    gate("security audit", [py, "data/scripts/cm_lab_security.py", "--check"], int(ExitCode.SECURITY))

    # human-data guard (in-process)
    try:
        human_data_guard.assert_clean(root)
        _print_check(True, "human-data guard")
        results.append(("human-data guard", True, int(ExitCode.HUMAN_GATE)))
    except human_data_guard.HumanGateViolationError as exc:
        _print_check(False, "human-data guard", str(exc))
        results.append(("human-data guard", False, int(ExitCode.HUMAN_GATE)))

    if args.with_tests:
        gate("tests (pytest full)", [py, "-m", "pytest", "tests/", "-q"], int(ExitCode.VALIDATION))

    failed = [(n, c) for n, ok, c in results if not ok]
    print()
    if not failed:
        print(f"VALIDATE: PASS ({len(results)} checks green)")
        return int(ExitCode.OK)
    # Return the most severe failure code (human-gate > security > artifact > other)
    severity = {int(ExitCode.HUMAN_GATE): 4, int(ExitCode.SECURITY): 3,
                int(ExitCode.ARTIFACT_MISMATCH): 2}
    worst = max(failed, key=lambda nc: (severity.get(nc[1], 1), nc[1]))[1]
    print(f"VALIDATE: FAIL ({len(failed)} check(s)): {', '.join(n for n, _ in failed)}")
    return int(worst)


# --------------------------------------------------------------------------- #
# claims verify / artifacts verify / security scan
# --------------------------------------------------------------------------- #
def _cmd_claims(args: argparse.Namespace) -> int:
    py = _python()
    ok, rc, tail = _run("claims graph", [py, "data/scripts/cm_lab_claims_graph.py", "--check"])
    _print_check(ok, "claims verify", tail)
    return int(ExitCode.OK) if ok else int(ExitCode.VALIDATION)


def _cmd_artifacts(args: argparse.Namespace) -> int:
    py = _python()
    ok, rc, tail = _run("registry integrity", [py, "data/scripts/cm_lab_registry.py", "--check"])
    _print_check(ok, "artifacts verify", tail)
    return int(ExitCode.OK) if ok else int(ExitCode.ARTIFACT_MISMATCH)


def _cmd_security(args: argparse.Namespace) -> int:
    py = _python()
    root = _repo_root()
    ok, rc, tail = _run("security audit", [py, "data/scripts/cm_lab_security.py", "--check"])
    _print_check(ok, "security audit", tail)
    try:
        human_data_guard.assert_clean(root)
        _print_check(True, "human-data guard")
        guard_ok = True
    except human_data_guard.HumanGateViolationError as exc:
        _print_check(False, "human-data guard", str(exc))
        guard_ok = False
    if ok and guard_ok:
        print("SECURITY: PASS")
        return int(ExitCode.OK)
    print("SECURITY: FAIL")
    return int(ExitCode.HUMAN_GATE) if not guard_ok else int(ExitCode.SECURITY)


# --------------------------------------------------------------------------- #
# demo / reproduce
# --------------------------------------------------------------------------- #
_REPRODUCE = {
    "cm8": "data/scripts/cm8_no_drift.py",
    "deep-dive": "data/scripts/cm_deep_dive_runner.py",
    "leakage": "data/scripts/cm_leakage_scan.py",
}


def _cmd_demo(args: argparse.Namespace) -> int:
    py = _python()
    ok, rc, tail = _run("demo", [py, "data/scripts/cm_deep_dive_runner.py", "--demo"], timeout=3600)
    _print_check(ok, "demo", tail)
    return int(ExitCode.OK) if ok else int(ExitCode.GENERIC)


def _cmd_reproduce(args: argparse.Namespace) -> int:
    py = _python()
    root = _repo_root()
    script = _REPRODUCE.get(args.name, args.name)
    if not (root / script).is_file():
        print(f"reproduce: unknown target {args.name!r} (known: {', '.join(_REPRODUCE)})")
        return int(ExitCode.USAGE)
    ok, rc, tail = _run(f"reproduce {args.name}", [py, script], timeout=7200)
    _print_check(ok, f"reproduce {args.name}", tail)
    return int(ExitCode.OK) if ok else int(ExitCode.REPRODUCIBILITY)


# --------------------------------------------------------------------------- #
# registration
# --------------------------------------------------------------------------- #
def register(sub: argparse._SubParsersAction) -> None:
    """Attach the research subcommands to the ``cm`` parser."""
    sub.add_parser("doctor", help="environment/dependency/path/data diagnostics").set_defaults(func=_cmd_doctor)

    v = sub.add_parser("validate", help="run the scientific-integrity gates")
    v.add_argument("--with-tests", action="store_true", help="also run the full pytest suite")
    v.set_defaults(func=_cmd_validate)

    c = sub.add_parser("claims", help="claim registry operations")
    c_sub = c.add_subparsers(dest="action", required=True)
    c_sub.add_parser("verify").set_defaults(func=_cmd_claims)

    a = sub.add_parser("artifacts", help="frozen artifact operations")
    a_sub = a.add_subparsers(dest="action", required=True)
    a_sub.add_parser("verify").set_defaults(func=_cmd_artifacts)

    sec = sub.add_parser("security", help="security operations")
    sec_sub = sec.add_subparsers(dest="action", required=True)
    sec_sub.add_parser("scan").set_defaults(func=_cmd_security)

    sub.add_parser("demo", help="run the fast demo pipeline").set_defaults(func=_cmd_demo)

    r = sub.add_parser("reproduce", help="run a named reproduction")
    r.add_argument("name", help="cm8 | deep-dive | leakage | <script path>")
    r.set_defaults(func=_cmd_reproduce)
