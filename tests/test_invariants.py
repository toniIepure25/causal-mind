"""Scientific invariant tests — properties that must NEVER regress.

These are not unit tests of a function; they are guards on the scientific record.
Each test fails LOUDLY if a frozen property, a frozen config value, or a structural
guarantee changes. Run with the rest of the suite: ``pytest tests/test_invariants.py``.

Invariants covered:
  - CM-2: held-out subjects remain subject-disjoint (no subject in >1 split).
  - CM-3: future targets are strictly prospective (all horizons > 0).
  - CM-5: HRF safety buffer respected (buffer 6 s, window 15 s).
  - CM-6: an unidentified counterfactual cannot be labeled causal (engine refuses).
  - CM-7: randomization-aware inference preserved (list-level randomized design).
  - CM-8: confirmatory alpha remains 0.05.
  - CM-8: basin tail remains 0.10.
  - CM-8: primary BRP definition + predicted_basin.py SHA unchanged.
  - CM-8: no real human-data collection enabled pre-ethics (synthetic pseudonyms only).
  - CM-9A: synthetic results are isolated from the empirical claims registry.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(rel: str) -> dict:
    p = ROOT / rel
    assert p.exists(), f"frozen artifact missing: {rel}"
    return json.loads(p.read_text(encoding="utf-8"))


def _sha256(rel: str) -> str:
    p = ROOT / rel
    assert p.exists(), f"frozen file missing: {rel}"
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# CM-2: subject-disjoint split
# --------------------------------------------------------------------------- #
def test_cm2_split_is_subject_disjoint():
    seal = _load("data/manifests/cm2_split_seal.json")
    splits = seal["split"]
    train, val, test = set(splits["train"]), set(splits["val"]), set(splits["test"])
    assert not (train & val), "CM-2: a subject appears in both train and val"
    assert not (train & test), "CM-2: a subject appears in both train and test"
    assert not (val & test), "CM-2: a subject appears in both val and test"
    # The split sizes must match the frozen protocol.
    assert (len(train), len(val), len(test)) == (83, 18, 17), (
        "CM-2: split sizes changed from the frozen 83/18/17"
    )


# --------------------------------------------------------------------------- #
# CM-3: strictly prospective targets
# --------------------------------------------------------------------------- #
def test_cm3_targets_are_strictly_prospective():
    proto = _load("data/manifests/cm3_protocol_seal.json")["protocol"]
    horizons = proto["event_horizons"]
    assert horizons, "CM-3: no event horizons declared"
    assert all(h > 0 for h in horizons), (
        f"CM-3: a non-positive horizon {horizons} would make the target non-prospective"
    )


# --------------------------------------------------------------------------- #
# CM-5: HRF safety buffer
# --------------------------------------------------------------------------- #
def test_cm5_hrf_safe_buffer_respected():
    proto = _load("data/manifests/cm5_protocol_seal.json")["protocol"]
    assert proto["hrf_safe_buffer_s"] == 6.0, "CM-5: HRF-safe buffer changed from 6 s"
    assert proto["neural_history_window_s"] == 15.0, (
        "CM-5: neural history window changed from 15 s"
    )
    # The decisive contrast must remain M4 - M2 (neural incremental value).
    assert proto["decisive_contrast"] == "M4_minus_M2", (
        "CM-5: decisive contrast changed from M4_minus_M2"
    )


# --------------------------------------------------------------------------- #
# CM-6: unidentified counterfactual cannot be labeled causal
# --------------------------------------------------------------------------- #
def test_cm6_unidentified_counterfactual_refused():
    from causal_mind.causal.counterfactuals import (
        CounterfactualResult,
        RandomizedEvidence,
    )

    # No randomized evidence -> must REFUSE 'experimentally_identified'.
    with pytest.raises(ValueError):
        CounterfactualResult(
            estimand="P(Y|do(X))",
            value=0.1,
            counterfactual_status="experimentally_identified",
            evidence=None,
        )
    # Non-randomized evidence -> must also refuse.
    with pytest.raises(ValueError):
        CounterfactualResult(
            estimand="P(Y|do(X))",
            value=0.1,
            counterfactual_status="experimentally_identified",
            evidence=RandomizedEvidence(experiment_id="x", randomized=False, n=10),
        )
    # A valid randomized record IS allowed (the method works when it should).
    ok = CounterfactualResult(
        estimand="P(Y|do(X))",
        value=0.1,
        counterfactual_status="experimentally_identified",
        evidence=RandomizedEvidence(experiment_id="cm7", randomized=True, n=20),
    )
    assert ok.is_causal_claim


# --------------------------------------------------------------------------- #
# CM-7: randomization-aware inference preserved
# --------------------------------------------------------------------------- #
def test_cm7_randomization_aware_inference():
    res = _load("reports/cm7_results.json")
    # The primary ATE must carry a permutation p from the randomized design.
    ate = res["primary_ate"]
    assert "p_permutation_2phase" in ate, "CM-7: permutation p missing from primary ATE"
    assert ate["n_subjects"] == 20, "CM-7: subject count changed from 20"
    # The decision must remain the validated null (method validated, effect null).
    assert res["decision"] == "CM7_NULL_NO_RECOVERABLE_CAUSAL_EFFECT", (
        "CM-7: decision state changed"
    )


# --------------------------------------------------------------------------- #
# CM-8: confirmatory alpha remains 0.05
# --------------------------------------------------------------------------- #
def test_cm8_confirmatory_alpha_is_005():
    cfg = _load("docs/ethics/cm8_software_freeze_manifest.json")["config"]
    assert cfg["test_alpha"] == 0.05, "CM-8: confirmatory alpha changed from 0.05"
    assert cfg["b_permutation_confirmatory"] == 10000, (
        "CM-8: confirmatory permutation count changed from 10000"
    )


# --------------------------------------------------------------------------- #
# CM-8: basin tail remains 0.10 (in BOTH frozen config locations)
# --------------------------------------------------------------------------- #
def test_cm8_basin_tail_is_010():
    forecaster = _load("artifacts/cm8_forecaster/config.json")
    freeze = _load("docs/ethics/cm8_software_freeze_manifest.json")["config"]
    assert forecaster["basin_tail"] == 0.1, "CM-8: forecaster basin_tail changed from 0.1"
    assert freeze["basin_tail"] == 0.1, "CM-8: freeze-manifest basin_tail changed from 0.1"
    assert forecaster["basin_tail"] == freeze["basin_tail"], (
        "CM-8: basin_tail inconsistent between forecaster config and freeze manifest"
    )


# --------------------------------------------------------------------------- #
# CM-8: primary BRP definition + predicted_basin.py SHA unchanged
# --------------------------------------------------------------------------- #
def test_cm8_brp_definition_and_code_unchanged():
    forecaster = _load("artifacts/cm8_forecaster/config.json")
    # The BRP definition string must remain the frozen one.
    assert "outside the basin" in forecaster["inference"]["brp"], (
        "CM-8: BRP definition changed"
    )
    assert forecaster["primary_horizon_h_star"] == 2, (
        "CM-8: primary horizon h* changed from 2"
    )
    # The basin/BRP code SHA must match the software freeze manifest.
    freeze = _load("docs/ethics/cm8_software_freeze_manifest.json")
    expected_sha = freeze["code"]["src/causal_mind/causal/predicted_basin.py"]["sha256"]
    actual_sha = _sha256("src/causal_mind/causal/predicted_basin.py")
    assert actual_sha == expected_sha, (
        "CM-8: predicted_basin.py changed since the software freeze "
        f"(expected {expected_sha[:12]}…, got {actual_sha[:12]}…)"
    )


# --------------------------------------------------------------------------- #
# CM-8: no real human-data collection enabled pre-ethics
# --------------------------------------------------------------------------- #
def test_cm8_no_real_human_data_pre_ethics():
    man = _load("data/manifests/cm8_randomization_manifest.json")
    # The randomization manifest uses SYNTHETIC pseudonyms (P-XXX), never real IDs.
    for pid, seq in man["manifests"].items():
        assert pid.startswith("P-"), f"CM-8: non-pseudonym participant id {pid!r}"
        assert len(seq) == 24, f"CM-8: {pid} does not have 24 trials"
        assert set(seq) <= {"control", "sham", "general", "cue"}, (
            f"CM-8: {pid} has an unexpected condition"
        )
    assert man["n_subjects"] == 20, "CM-8: randomization n_subjects changed from 20"
    assert man["seed"] == 20260917, "CM-8: randomization seed changed from 20260917"
    # No real participant-data directory may exist in the repo.
    assert not (ROOT / "data" / "participants").exists(), (
        "CM-8: a real participant-data directory exists pre-ethics"
    )


# --------------------------------------------------------------------------- #
# CM-9A: synthetic results isolated from empirical claims
# --------------------------------------------------------------------------- #
def test_cm9a_synthetic_isolated_from_empirical_claims():
    lab = _load("reports/cm9a_oracle_lab/cm9a_oracle_lab.json")
    # The lab must report a synthetic-only state.
    assert lab["state"] == "CM9A_SYNTHETIC_ORACLE_READY", (
        "CM-9A: oracle lab state changed"
    )
    # The claims registry must mark C-012 as synthetic / design-only (not empirical).
    registry = (ROOT / "docs" / "claims_registry.md").read_text(encoding="utf-8")
    c012 = next(
        (ln for ln in registry.splitlines() if ln.strip().startswith("| C-012")), None
    )
    assert c012 is not None, "claims registry: C-012 row missing"
    assert "synthetic" in c012.lower(), (
        "CM-9A: C-012 is no longer marked as a synthetic (non-empirical) claim"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
