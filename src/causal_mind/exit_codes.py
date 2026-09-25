"""Exit-code contract (CM-REPO S16).

Stable, documented exit codes for CLI entry points and validation scripts.
``0`` means success. Non-zero values are stable and safe to branch on in CI,
pre-commit hooks, and the ``cm`` CLI. Do not renumber; append new codes.
"""
from __future__ import annotations

from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    GENERIC = 1
    VALIDATION = 2
    ENVIRONMENT = 3
    PROTOCOL_VIOLATION = 4
    ARTIFACT_MISMATCH = 5
    LEAKAGE = 6
    FROZEN_CONFIG_MUTATION = 7
    HUMAN_GATE = 8
    DATA_INTEGRITY = 9
    REPRODUCIBILITY = 10
    SECURITY = 11
    NOT_FOUND = 12
    USAGE = 13


def describe(code: int) -> str:
    """Human-readable description for an exit code (for CLI --help / logs)."""
    try:
        return ExitCode(code).name.lower().replace("_", " ")
    except ValueError:
        return f"unknown ({code})"
