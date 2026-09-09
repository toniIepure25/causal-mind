from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


def _git_sha(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-c", "safe.directory=*", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=20,
        )
        return result.stdout.strip() or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def collect_environment() -> dict[str, str]:
    env: dict[str, str] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
    }
    for module in ("numpy", "pandas", "scipy", "sklearn", "torch"):
        try:
            mod = __import__(module)
            env[module] = str(getattr(mod, "__version__", "unknown"))
        except ImportError:
            env[module] = "absent"
    return env


class ExperimentManifest(BaseModel):
    exp_id: str
    hypothesis: str | None = None
    git_sha: str
    config: dict[str, object] = Field(default_factory=dict)
    dataset_version: str | None = None
    dataset_checksum: str | None = None
    split: dict[str, object] = Field(default_factory=dict)
    seed: int | None = None
    model: str | None = None
    environment: dict[str, str] = Field(default_factory=dict)
    metrics: dict[str, object] = Field(default_factory=dict)
    wall_time_s: float | None = None
    audit_status: str = "pending"
    created: str = Field(
        default_factory=lambda: datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    )


def config_hash(config: dict[str, object]) -> str:
    blob = json.dumps(config, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def write_manifest(path: Path, manifest: ExperimentManifest) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(manifest.model_dump(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def read_manifest(path: Path) -> ExperimentManifest:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ExperimentManifest.model_validate(data)
