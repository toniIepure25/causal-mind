"""Centralized path discovery (CM-REPO S9).

Library code must never hard-code an absolute pod path. The repository root is
discovered by walking up from this module to the directory containing
``pyproject.toml``. Deployment can override with environment variables:

  CM_REPO_ROOT  -- explicit repository root (highest priority)
  CM_DATA_ROOT  -- explicit data root (default ``<repo_root>/data``)

Infrastructure-only env vars (``HF_HOME``, ``TORCH_HOME``, ...) are set by the
bootstrap/runbook; this module only provides a portable, overridable fallback.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def repo_root() -> Path:
    """The causal-mind-v2 repository root (overridable via ``CM_REPO_ROOT``)."""
    env = os.environ.get("CM_REPO_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    # Fallback: this file lives at <root>/src/causal_mind/paths.py
    return here.parents[2]


def data_root() -> Path:
    """The ``data/`` directory (overridable via ``CM_DATA_ROOT``)."""
    env = os.environ.get("CM_DATA_ROOT")
    if env:
        return Path(env).resolve()
    return repo_root() / "data"


def manifests_dir() -> Path:
    return data_root() / "manifests"


def derived_dir() -> Path:
    return data_root() / "derived"


def thought_events_dir() -> Path:
    return derived_dir() / "thought_events"


def embeddings_dir() -> Path:
    return data_root() / "embeddings"


def raw_dir() -> Path:
    return data_root() / "raw"


def artifacts_dir() -> Path:
    return repo_root() / "artifacts"


def cm2_split_seal() -> Path:
    return manifests_dir() / "cm2_split_seal.json"


def cm8_config() -> Path:
    return artifacts_dir() / "cm8_forecaster" / "config.json"


def hf_home() -> str:
    """Portable, overridable HuggingFace cache location (infrastructure)."""
    return os.environ.get("CM_HF_HOME", str(Path.home() / ".hf-home"))
