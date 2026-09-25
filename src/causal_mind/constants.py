"""Centralized scientific constants (CM-REPO S8).

Single source of truth. These constants are READ from the frozen config/seal
files, never re-hard-coded. If a frozen file is missing or malformed, this
raises :class:`NotFoundError` / :class:`DataIntegrityError` rather than
silently substituting a default, so code can never drift from the frozen
protocol.

Namespaces (all lazy-loaded and cached)::

    from causal_mind import constants
    constants.cm8().horizons      # (1, 2, 3, 4, 5, 6, 8, 10)
    constants.cm8().h_star        # 2
    constants.cm2().seed          # 20260911
    constants.cm3().event_horizons

Frozen sources:
* CM-8  -> artifacts/cm8_forecaster/config.json
* CM-2  -> data/manifests/cm2_split_seal.json
* CM-3  -> data/manifests/cm3_protocol_seal.json
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from causal_mind import paths
from causal_mind.errors import DataIntegrityError, NotFoundError


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise NotFoundError(f"frozen config not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise DataIntegrityError(
            f"frozen config is not valid JSON: {path}", details={"error": str(exc)}
        ) from exc


def _require(cfg: dict, key: str, path: Path):
    if key not in cfg:
        raise DataIntegrityError(
            f"frozen config {path} is missing required key {key!r}"
        )
    return cfg[key]


@dataclass(frozen=True)
class CM8:
    """CM-8 confirmatory forecaster (frozen)."""

    architecture: str
    k: int
    ridge_alpha: float
    horizons: tuple[int, ...]
    h_star: int
    basin_tail: float
    split_seed: int
    encoder: str
    encoder_dim: int
    n_train: int
    n_val: int
    n_test: int
    raw: dict


@lru_cache(maxsize=1)
def cm8() -> CM8:
    p = paths.cm8_config()
    cfg = _load_json(p)
    split = _require(cfg, "split", p)
    return CM8(
        architecture=_require(cfg, "architecture", p),
        k=int(_require(cfg, "k_history_depth", p)),
        ridge_alpha=float(_require(cfg, "ridge_alpha", p)),
        horizons=tuple(int(h) for h in _require(cfg, "horizons", p)),
        h_star=int(_require(cfg, "primary_horizon_h_star", p)),
        basin_tail=float(_require(cfg, "basin_tail", p)),
        split_seed=int(_require(cfg, "split_seed", p)),
        encoder=_require(cfg, "semantic_encoder", p),
        encoder_dim=int(_require(cfg, "encoder_dim", p)),
        n_train=int(split["train"]),
        n_val=int(split["val"]),
        n_test=int(split["test"]),
        raw=cfg,
    )


@dataclass(frozen=True)
class CM2:
    """CM-2 subject-disjoint split seal (frozen)."""

    seal: str
    seed: int
    n_subjects: int
    train: tuple[str, ...]
    val: tuple[str, ...]
    test: tuple[str, ...]
    raw: dict


@lru_cache(maxsize=1)
def cm2() -> CM2:
    p = paths.cm2_split_seal()
    cfg = _load_json(p)
    split = _require(cfg, "split", p)
    return CM2(
        seal=_require(cfg, "seal", p),
        seed=int(_require(cfg, "seed", p)),
        n_subjects=int(_require(cfg, "n_subjects", p)),
        train=tuple(split["train"]),
        val=tuple(split["val"]),
        test=tuple(split["test"]),
        raw=cfg,
    )


@dataclass(frozen=True)
class CM3:
    """CM-3 evaluation protocol seal (frozen)."""

    seal: str
    anchor_commit: str
    event_horizons: tuple[int, ...]
    time_horizons_s: tuple[int, ...]
    targets: tuple[str, ...]
    baselines: tuple[str, ...]
    tph_rules: tuple[str, ...]
    nulls: tuple[str, ...]
    raw: dict


@lru_cache(maxsize=1)
def cm3() -> CM3:
    p = paths.manifests_dir() / "cm3_protocol_seal.json"
    cfg = _load_json(p)
    proto = _require(cfg, "protocol", p)
    return CM3(
        seal=_require(cfg, "seal", p),
        anchor_commit=_require(proto, "anchor_commit", p),
        event_horizons=tuple(int(h) for h in _require(proto, "event_horizons", p)),
        time_horizons_s=tuple(int(h) for h in _require(proto, "time_horizons_s", p)),
        targets=tuple(_require(proto, "targets", p)),
        baselines=tuple(_require(proto, "baselines", p)),
        tph_rules=tuple(_require(proto, "tph_rules", p)),
        nulls=tuple(_require(proto, "nulls", p)),
        raw=cfg,
    )
