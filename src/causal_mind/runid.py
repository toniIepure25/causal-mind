"""Run identifiers (CM-REPO S15).

Every experiment run gets a stable, sortable, traceable run ID of the form::

    cm-<experiment>-<UTCstamp>-<shortsha>
    e.g. cm-cm8-20260925T120000Z-a1b2c3d

The ID is written to the run's output manifest so any artifact can be traced
back to the exact run (git SHA, timestamp, seed) that produced it. Set
``CM_RUN_ID`` to reuse an externally assigned ID (e.g. from CI).
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import os
import uuid


def utc_stamp() -> str:
    """Current UTC time as a compact sortable stamp, e.g. 20260925T120000Z."""
    return _dt.datetime.now(_dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def short_sha(seed: str, n: int = 7) -> str:
    """Deterministic short hex digest of a seed string."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:n]


def make_run_id(experiment: str, *, seed: str | None = None) -> str:
    """Build a run ID. Reuses ``CM_RUN_ID`` if already set (idempotent)."""
    existing = os.environ.get("CM_RUN_ID")
    if existing:
        return existing
    s = seed or f"{experiment}-{utc_stamp()}-{uuid.uuid4().hex[:8]}"
    return f"cm-{experiment}-{utc_stamp()}-{short_sha(s)}"


def run_id() -> str | None:
    """The active run ID from the environment, or None."""
    return os.environ.get("CM_RUN_ID")
