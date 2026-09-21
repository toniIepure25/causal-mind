"""CM-LAB registries: data lineage, artifact registry, experiment registry.

Generates three machine-readable registries plus a human-readable report, and (with
``--check``) verifies that no frozen artifact has changed since it was registered.

Outputs:
    registries/lineage.json            (S9  data lineage)
    registries/artifact_registry.json  (S10 artifact registry)
    registries/experiment_registry.json (S11 experiment registry)
    reports/registry_report.md        (human-readable)

Usage:
    .venv/bin/python data/scripts/cm_lab_registry.py            # build + write
    .venv/bin/python data/scripts/cm_lab_registry.py --check    # verify frozen SHAs (CI)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REG = ROOT / "registries"
LINEAGE = REG / "lineage.json"
ARTIFACTS = REG / "artifact_registry.json"
EXPERIMENTS = REG / "experiment_registry.json"
REPORT = ROOT / "reports" / "registry_report.md"
FREEZE_SHA = "8a9d5dd00c0d62ab6ba18e7a3ae28fbc74a85e14"


def sha256(rel: str) -> str:
    p = ROOT / rel
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# Frozen artifacts (S10). Each: name, version, path, status, frozen, command,
# input manifests, producing commit.
# --------------------------------------------------------------------------- #
ARTIFACT_DEFS = [
    {"name": "cm8_forecaster_config", "version": "1.0", "path": "artifacts/cm8_forecaster/config.json",
     "status": "frozen", "frozen": True, "command": "cm8_forecaster build (frozen)",
     "inputs": ["data/manifests/cm2_split_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm8_forecasting_freeze_manifest", "version": "1.0", "path": "artifacts/cm8_forecasting_freeze_manifest.json",
     "status": "frozen", "frozen": True, "command": "cm8_forecaster freeze",
     "inputs": ["artifacts/cm8_forecaster/config.json"], "commit": FREEZE_SHA},
    {"name": "cm2_split_seal", "version": "1.0", "path": "data/manifests/cm2_split_seal.json",
     "status": "frozen", "frozen": True, "command": "data/scripts/run_full_evaluation.py",
     "inputs": ["data/manifests/ds006067_manifest.yaml"], "commit": FREEZE_SHA},
    {"name": "cm3_protocol_seal", "version": "1.0", "path": "data/manifests/cm3_protocol_seal.json",
     "status": "frozen", "frozen": True, "command": "data/scripts/seal_cm3_protocol.py",
     "inputs": ["data/manifests/cm2_split_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm5_protocol_seal", "version": "1.0", "path": "data/manifests/cm5_protocol_seal.json",
     "status": "frozen", "frozen": True, "command": "data/scripts/seal_cm5_protocol.py",
     "inputs": ["data/manifests/cm2_split_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm8_randomization_manifest", "version": "1.0", "path": "data/manifests/cm8_randomization_manifest.json",
     "status": "frozen", "frozen": True, "command": "cm8 randomization (seed 20260917)",
     "inputs": [], "commit": FREEZE_SHA},
    {"name": "cm8_software_freeze_manifest", "version": "1.0", "path": "docs/ethics/cm8_software_freeze_manifest.json",
     "status": "frozen", "frozen": True, "command": "cm8r software freeze",
     "inputs": ["artifacts/cm8_forecaster/config.json"], "commit": FREEZE_SHA},
    {"name": "cm2_results", "version": "1.0", "path": "reports/cm2_results.json",
     "status": "validated", "frozen": True, "command": "data/scripts/run_full_evaluation.py",
     "inputs": ["data/manifests/cm2_split_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm3_results", "version": "1.0", "path": "reports/cm3_results.json",
     "status": "validated", "frozen": True, "command": "data/scripts/run_cm3_evaluation.py",
     "inputs": ["data/manifests/cm3_protocol_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm5_decisive_results", "version": "1.0", "path": "reports/cm5_decisive_results.json",
     "status": "validated (null)", "frozen": True, "command": "data/scripts/run_cm5_decisive.py",
     "inputs": ["data/manifests/cm5_protocol_seal.json"], "commit": FREEZE_SHA},
    {"name": "cm6_observational_results", "version": "1.0", "path": "reports/cm6_observational_results.json",
     "status": "validated (no identification)", "frozen": True, "command": "data/scripts/cm6_observational_analysis.py",
     "inputs": ["data/manifests/ds006067_manifest.yaml"], "commit": FREEZE_SHA},
    {"name": "cm7_results", "version": "1.0", "path": "reports/cm7_results.json",
     "status": "validated (null)", "frozen": True, "command": "data/scripts/cm7_analyze.py",
     "inputs": ["data/manifests/ds005494_manifest.json"], "commit": FREEZE_SHA},
]


# --------------------------------------------------------------------------- #
# Data lineage (S9). Transformation DAG of major derived objects.
# --------------------------------------------------------------------------- #
LINEAGE_DEFS = [
    {"id": "ds006067_raw", "type": "raw", "parents": [], "output": "data/manifests/ds006067_manifest.yaml",
     "transform": "acquisition + 10/10 integrity checks", "note": "OpenNeuro MRI + OSF a56rm; 118 subjects"},
    {"id": "embeddings_miniLM", "type": "derived", "parents": ["ds006067_raw"], "output": "artifacts/cm8_forecaster/config.json",
     "transform": "all-MiniLM-L6-v2 (dim 384) on thought text", "note": "frozen encoder"},
    {"id": "cm2_split", "type": "derived", "parents": ["embeddings_miniLM"], "output": "data/manifests/cm2_split_seal.json",
     "transform": "subject-disjoint 83/18/17 split (seed 20260911)", "note": "seal 67505261"},
    {"id": "cm2_results", "type": "result", "parents": ["cm2_split"], "output": "reports/cm2_results.json",
     "transform": "held-out semantic cosine vs baselines B0-B7", "note": "0.3623 [0.3523,0.3720]"},
    {"id": "cm3_protocol", "type": "derived", "parents": ["cm2_split"], "output": "data/manifests/cm3_protocol_seal.json",
     "transform": "prospective horizons 1..10 (all >0)", "note": "CM-3 protocol seal"},
    {"id": "cm3_results", "type": "result", "parents": ["cm3_protocol"], "output": "reports/cm3_results.json",
     "transform": "PredictiveGain per horizon", "note": "monotonic decay"},
    {"id": "cm5_protocol", "type": "derived", "parents": ["cm2_split"], "output": "data/manifests/cm5_protocol_seal.json",
     "transform": "HRF-safe alignment (buffer 6s, window 15s)", "note": "CM-5 protocol seal"},
    {"id": "cm5_results", "type": "result", "parents": ["cm5_protocol"], "output": "reports/cm5_decisive_results.json",
     "transform": "incremental neural gain M4-M2", "note": "clean null (0/16 positive)"},
    {"id": "cm6_results", "type": "result", "parents": ["ds006067_raw"], "output": "reports/cm6_observational_results.json",
     "transform": "observational SCM identifiability", "note": "0/84 identifiable"},
    {"id": "ds005494_raw", "type": "raw", "parents": [], "output": "data/manifests/ds005494_manifest.json",
     "transform": "public intervention dataset v1.0.1", "note": "20 subjects, 3330 pairs"},
    {"id": "cm7_results", "type": "result", "parents": ["ds005494_raw"], "output": "reports/cm7_results.json",
     "transform": "list-level randomized ATE + 2-phase permutation", "note": "valid null, method validated"},
    {"id": "cm8_randomization", "type": "derived", "parents": [], "output": "data/manifests/cm8_randomization_manifest.json",
     "transform": "counterbalanced round-robin (seed 20260917)", "note": "20 subjects x 24 trials"},
    {"id": "cm8_forecaster", "type": "derived", "parents": ["cm2_split"], "output": "artifacts/cm8_forecaster/config.json",
     "transform": "ridge forecaster (k=3, alpha=100) frozen", "note": "BRP at h*=2, basin_tail 0.1"},
]


# --------------------------------------------------------------------------- #
# Experiment registry (S11).
# --------------------------------------------------------------------------- #
EXPERIMENT_DEFS = [
    {"id": "CM-2", "hypothesis": "Past thought history predicts next-thought semantics above baselines.",
     "status": "validated", "design": "confirmatory (subject-disjoint)", "dataset": "ds006067",
     "split": "83/18/17", "primary_endpoint": "held_out_semantic_cosine",
     "config": "data/manifests/cm2_split_seal.json", "code_sha": FREEZE_SHA,
     "result": "0.3623 [0.3523,0.3720] > 0.3167 (B7)", "decision": "CM2_PASS", "claim_ids": ["C-003"]},
    {"id": "CM-3", "hypothesis": "Cognitive history predicts future thought semantics at every horizon.",
     "status": "validated", "design": "confirmatory (prospective)", "dataset": "ds006067",
     "split": "83/18/17", "primary_endpoint": "predictive_gain_per_horizon",
     "config": "data/manifests/cm3_protocol_seal.json", "code_sha": FREEZE_SHA,
     "result": "gain>0 at all h=1..10, monotonic decay", "decision": "CM3_PASS", "claim_ids": ["C-004"]},
    {"id": "CM-5", "hypothesis": "HRF-safe BOLD adds incremental predictive value for target content.",
     "status": "validated (null)", "design": "confirmatory", "dataset": "ds006067",
     "split": "73/17/16", "primary_endpoint": "incremental_neural_gain_M4_minus_M2",
     "config": "data/manifests/cm5_protocol_seal.json", "code_sha": FREEZE_SHA,
     "result": "N2 ~ -0.09 at all horizons, 0/16 subjects positive", "decision": "CM5_NULL", "claim_ids": ["C-005"]},
    {"id": "CM-6", "hypothesis": "An observational SCM of ds006067 yields identifiable causal edges.",
     "status": "validated (no identification)", "design": "exploratory (observational)", "dataset": "ds006067",
     "split": "n/a", "primary_endpoint": "n_identifiable_edges",
     "config": "reports/cm6_observational_results.json", "code_sha": FREEZE_SHA,
     "result": "0/84 identifiable (unmeasured confounding)", "decision": "CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION", "claim_ids": ["C-006", "C-009"]},
    {"id": "CM-7", "hypothesis": "The framework correctly identifies + estimates a randomized causal effect.",
     "status": "validated (null)", "design": "confirmatory (randomized)", "dataset": "ds005494",
     "split": "list-level within-subject", "primary_endpoint": "ate_2phase_permutation",
     "config": "docs/cm7_protocol.md", "code_sha": FREEZE_SHA,
     "result": "ATE -0.0386, p=0.0733 (valid null)", "decision": "CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT", "claim_ids": ["C-010"]},
    {"id": "CM-8", "hypothesis": "Pre-human readiness: forecaster frozen, ghost pilot passes, MC calibrated, engine offline.",
     "status": "validated (pre-human)", "design": "pre-pilot hardening (NO human data)", "dataset": "ds006067 (ghost replay)",
     "split": "n/a", "primary_endpoint": "readiness_gates",
     "config": "docs/ethics/cm8_software_freeze_manifest.json", "code_sha": FREEZE_SHA,
     "result": "10/10 gates; clean-room bit-identical", "decision": "CM8R_PREHUMAN_HARDENED", "claim_ids": ["C-011"]},
    {"id": "CM-9A", "hypothesis": "Synthetic Oracle lab: oracle conditions x agent policies, RPR/PIE measured.",
     "status": "design-only (synthetic)", "design": "synthetic exploration (NO human data)", "dataset": "synthetic",
     "split": "n/a", "primary_endpoint": "rpr_pie",
     "config": "src/causal_mind/oracle/", "code_sha": FREEZE_SHA,
     "result": "hidden_o5 RPR 1.48; veto_o0 RPR 0.16", "decision": "CM9A_SYNTHETIC_ORACLE_READY", "claim_ids": ["C-012"]},
]


def build() -> None:
    REG.mkdir(parents=True, exist_ok=True)
    # Artifact registry with computed SHAs.
    artifacts = []
    for a in ARTIFACT_DEFS:
        rec = dict(a)
        rec["sha256"] = sha256(a["path"])
        rec["config_hash"] = sha256(a["path"])  # config IS the artifact for config-type
        rec["environment_hash"] = "uv.lock"  # environment pinned by uv.lock
        artifacts.append(rec)
    ARTIFACTS.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.write_text(json.dumps({"version": "1.0", "freeze": FREEZE_SHA, "artifacts": artifacts},
                                    indent=2) + "\n", encoding="utf-8")

    # Data lineage with computed SHAs.
    lineage = []
    for l in LINEAGE_DEFS:
        rec = dict(l)
        rec["sha256"] = sha256(l["output"])
        lineage.append(rec)
    LINEAGE.parent.mkdir(parents=True, exist_ok=True)
    LINEAGE.write_text(json.dumps({"version": "1.0", "freeze": FREEZE_SHA, "lineage": lineage},
                                  indent=2) + "\n", encoding="utf-8")

    # Experiment registry.
    EXPERIMENTS.parent.mkdir(parents=True, exist_ok=True)
    EXPERIMENTS.write_text(json.dumps({"version": "1.0", "freeze": FREEZE_SHA, "experiments": EXPERIMENT_DEFS},
                                      indent=2) + "\n", encoding="utf-8")

    # Human-readable report.
    lines = ["# Registries (generated)", "",
             f"Freeze: `{FREEZE_SHA[:12]}`. Generated by `data/scripts/cm_lab_registry.py`.", "",
             "## Data lineage (S9)", "",
             "| node | type | parents | output | sha256[:12] |", "| --- | --- | --- | --- | --- |"]
    for l in lineage:
        lines.append(f"| {l['id']} | {l['type']} | {', '.join(l['parents']) or '-'} "
                     f"| `{l['output']}` | `{l['sha256'][:12]}` |")
    lines += ["", "## Artifact registry (S10)", "",
              "| artifact | status | frozen | sha256[:12] | command |", "| --- | --- | --- | --- | --- |"]
    for a in artifacts:
        lines.append(f"| {a['name']} | {a['status']} | {a['frozen']} | `{a['sha256'][:12]}` | `{a['command']}` |")
    lines += ["", "## Experiment registry (S11)", "",
              "| id | design | endpoint | decision | claims |", "| --- | --- | --- | --- | --- |"]
    for e in EXPERIMENT_DEFS:
        lines.append(f"| {e['id']} | {e['design']} | {e['primary_endpoint']} | {e['decision']} | {', '.join(e['claim_ids'])} |")
    lines.append("")
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"REGISTRIES: PASS (wrote {LINEAGE.name}, {ARTIFACTS.name}, {EXPERIMENTS.name}, {REPORT.name})")


def check() -> int:
    """Verify no frozen artifact changed since it was registered."""
    if not ARTIFACTS.exists():
        print("REGISTRIES: FAIL (artifact_registry.json missing; run build first)")
        return 1
    reg = json.loads(ARTIFACTS.read_text(encoding="utf-8"))
    failures = []
    for a in reg["artifacts"]:
        if not a.get("frozen"):
            continue
        actual = sha256(a["path"])
        if not actual:
            failures.append(f"{a['name']}: file missing ({a['path']})")
        elif actual != a["sha256"]:
            failures.append(f"{a['name']}: SHA changed (recorded {a['sha256'][:12]}…, actual {actual[:12]}…)")
    if failures:
        print("REGISTRIES: FAIL (frozen artifact integrity)")
        for f in failures:
            print(f"  - {f}")
        return 1
    n_frozen = sum(1 for a in reg["artifacts"] if a.get("frozen"))
    print(f"REGISTRIES: PASS ({n_frozen} frozen artifacts unchanged)")
    return 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
