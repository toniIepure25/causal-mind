"""Domain error taxonomy (CM-REPO S13).

Every failure mode a researcher or CI should be able to distinguish gets its
own exception type with a stable machine-readable ``code`` and a mapped exit
code (see :mod:`causal_mind.exit_codes`). All inherit from
:class:`CausalMindError`, so callers can catch the base class for generic
handling or a specific subclass for a specific failure.

Design rules:
* Raise the most specific type; never a bare ``Exception``.
* Always include a stable ``code`` and, where useful, a ``details`` dict so
  logs and CI can branch on machine-readable fields rather than parsing text.
* These are *domain* errors. Infrastructure errors (missing deps, disk full)
  should be wrapped in :class:`EnvironmentProblemError` with the cause chained.
"""
from __future__ import annotations

from typing import Any

from causal_mind.exit_codes import ExitCode


class CausalMindError(Exception):
    """Base class for all Causal Mind domain errors."""

    code = "CM_ERROR"
    exit_code = ExitCode.GENERIC

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "exit_code": int(self.exit_code),
            "details": self.details,
        }


class ValidationError(CausalMindError):
    """A validation gate failed (schema, invariant, or check)."""

    code = "CM_VALIDATION"
    exit_code = ExitCode.VALIDATION


class EnvironmentProblemError(CausalMindError):
    """The runtime environment is missing something (dep, path, service)."""

    code = "CM_ENVIRONMENT"
    exit_code = ExitCode.ENVIRONMENT


class ProtocolViolationError(CausalMindError):
    """A frozen protocol's invariants were violated (e.g. a split changed)."""

    code = "CM_PROTOCOL_VIOLATION"
    exit_code = ExitCode.PROTOCOL_VIOLATION


class ArtifactMismatchError(CausalMindError):
    """A frozen artifact's SHA-256 no longer matches its registry entry."""

    code = "CM_ARTIFACT_MISMATCH"
    exit_code = ExitCode.ARTIFACT_MISMATCH


class LeakageDetectedError(CausalMindError):
    """The leakage scanner found a test-set leak in a pipeline/report."""

    code = "CM_LEAKAGE"
    exit_code = ExitCode.LEAKAGE


class FrozenConfigMutationError(CausalMindError):
    """A frozen config/protocol file was modified after being sealed."""

    code = "CM_FROZEN_CONFIG_MUTATION"
    exit_code = ExitCode.FROZEN_CONFIG_MUTATION


class HumanGateViolationError(CausalMindError):
    """An action crossed a human/ethics gate (e.g. human data staged)."""

    code = "CM_HUMAN_GATE"
    exit_code = ExitCode.HUMAN_GATE


class DataIntegrityError(CausalMindError):
    """A dataset/manifest failed an integrity check (checksum, schema)."""

    code = "CM_DATA_INTEGRITY"
    exit_code = ExitCode.DATA_INTEGRITY


class ReproducibilityError(CausalMindError):
    """A run could not be reproduced (drift, missing seed, nondeterminism)."""

    code = "CM_REPRODUCIBILITY"
    exit_code = ExitCode.REPRODUCIBILITY


class SecurityError(CausalMindError):
    """A security scan failed (secret, unsafe pattern, or policy)."""

    code = "CM_SECURITY"
    exit_code = ExitCode.SECURITY


class NotFoundError(CausalMindError):
    """A required file, artifact, or registry entry does not exist."""

    code = "CM_NOT_FOUND"
    exit_code = ExitCode.NOT_FOUND
