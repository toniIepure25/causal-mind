from __future__ import annotations

from pathlib import Path

from causal_mind.utils.manifest import (
    ExperimentManifest,
    collect_environment,
    config_hash,
    read_manifest,
    write_manifest,
)


def test_manifest_roundtrip(tmp_path: Path) -> None:
    manifest = ExperimentManifest(
        exp_id="EXP-001",
        hypothesis="H1",
        git_sha="abc123",
        config={"model": "gru", "lr": 1e-3},
        dataset_version="ds006067@rev1",
        split={"train": ["s01"], "val": ["s02"], "test": ["s03"], "seed": [0]},
        seed=0,
        model="gru_category",
        environment=collect_environment(),
        metrics={"accuracy": 0.71, "permutation_pvalue": 0.01},
        wall_time_s=123.4,
    )
    path = tmp_path / "manifests" / "EXP-001.yaml"
    write_manifest(path, manifest)
    loaded = read_manifest(path)
    assert loaded.exp_id == "EXP-001"
    assert loaded.metrics["accuracy"] == 0.71
    assert loaded.git_sha == "abc123"
    assert loaded.audit_status == "pending"


def test_config_hash_stable() -> None:
    a = config_hash({"x": 1, "y": [1, 2]})
    b = config_hash({"y": [1, 2], "x": 1})
    assert a == b
    c = config_hash({"x": 2, "y": [1, 2]})
    assert a != c


def test_collect_environment_has_python() -> None:
    env = collect_environment()
    assert "python" in env
    assert "numpy" in env
