#!/usr/bin/env python3
"""CM-5 MRI cohort decision + seal (CM5-ELIG-1).

Applies the FROZEN eligibility criteria from configs/cm5_eligibility.json to:
  - reports/cm5_subject_eligibility.tsv  (metadata audit, A/B/C inputs)
  - reports/cm5_qc_audit.tsv             (confounds QC, D inputs)
  - data/manifests/cm5_bold_url_audit.tsv (BOLD URL-guard status, A1 input)
Produces:
  - reports/cm5_cohort_seal.json         (CM5_ELIGIBILITY_SEAL)
  - updated reports/cm5_subject_eligibility.tsv (final status columns)

Outcome-independent: no neural prediction metric is read or written.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path("/home/jovyan/work/causal-mind-v2")
CONFIG = ROOT / "configs" / "cm5_eligibility.json"
METADATA = ROOT / "reports" / "cm5_subject_eligibility.tsv"
QC = ROOT / "reports" / "cm5_qc_audit.tsv"
BOLD_URL = ROOT / "data" / "manifests" / "cm5_bold_url_audit.tsv"
SPLIT_SEAL = ROOT / "data" / "manifests" / "cm2_split_seal.json"
SEAL_OUT = ROOT / "reports" / "cm5_cohort_seal.json"


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    cfg = json.loads(CONFIG.read_text())
    c = cfg["constants"]
    min_targets = c["min_usable_targets"]
    d1 = cfg["criteria"]["D_motion_qc"]["D1_mean_fd_max_mm"]
    d2 = cfg["criteria"]["D_motion_qc"]["D2_frac_vol_fd_gt_1mm_max"]
    d3 = cfg["criteria"]["D_motion_qc"]["D3_frac_vol_fd_gt_2mm_max"]
    n_vol_expected = c["n_volumes"]

    meta = pd.read_csv(METADATA, sep="\t")
    qc = pd.read_csv(QC, sep="\t").set_index("subject_id")
    bold_url = pd.read_csv(BOLD_URL, sep="\t").set_index("subject")
    split_seal = json.loads(SPLIT_SEAL.read_text())
    split_of = {s: part for part in ("train", "val", "test")
                for s in split_seal["split"][part]}

    rows = []
    for _, r in meta.iterrows():
        sub = r["subject_id"]
        reasons = []
        # A1: BOLD retrievable with URL guard (from live API audit)
        bu = bold_url.loc[sub]
        if bu["status"] != "OK":
            reasons.append(f"A1_bold_url_guard({bu['status']})")
        # A2/A3/A4/B/C from metadata audit
        if r["eligibility_status"] == "EXCLUDED_METADATA":
            reasons.append(f"metadata({r['exclusion_reason']})")
        # B1/B2 from QC audit
        q = qc.loc[sub]
        if q["qc_status"] == "NO_CONFOUNDS":
            reasons.append("A3_confounds_unavailable")
        elif q["qc_status"] == "COMPUTED":
            if int(q["n_volumes"]) != n_vol_expected:
                reasons.append(f"B1_n_volumes({int(q['n_volumes'])})")
            if int(q["n_missing_core"]) > 0 or int(q["n_nonfinite_core"]) > 0:
                reasons.append("B2_confounds_missing")
            # D: motion
            if float(q["fd_mean"]) > d1:
                reasons.append(f"D1_mean_fd({q['fd_mean']}>{d1})")
            if float(q["fd_gt10_frac"]) > d2:
                reasons.append(f"D2_fd10frac({q['fd_gt10_frac']}>{d2})")
            if float(q["fd_gt20_frac"]) > d3:
                reasons.append(f"D3_fd20frac({q['fd_gt20_frac']}>{d3})")
        # C1: steady-state targets (AM-1)
        n_steady = int(r["steady_state_target_count"])
        if r["behavioral_available"] == 1 and n_steady < min_targets:
            reasons.append(f"C1_targets({n_steady}<{min_targets})")

        eligible = not reasons
        rows.append({
            "subject_id": sub,
            "cm3_split": r["cm3_split"],
            "eligible": int(eligible),
            "exclusion_reason": ";".join(reasons) or "-",
            "steady_state_target_count": n_steady,
        })

    final = pd.DataFrame(rows)
    # merge final status back into the metadata TSV
    meta["final_eligible"] = final.set_index("subject_id").loc[meta["subject_id"], "eligible"].values
    meta["final_exclusion_reason"] = final.set_index("subject_id").loc[meta["subject_id"], "exclusion_reason"].values
    meta.to_csv(METADATA, sep="\t", index=False)

    elig = final[final["eligible"] == 1]
    excl = final[final["eligible"] == 0]
    split_counts = {p: int((elig["cm3_split"] == p).sum()) for p in ("train", "val", "test")}

    # QC distribution snapshot (for the seal, per red-team demand)
    qcomp = qc[qc["qc_status"] == "COMPUTED"]
    def qdist(col):
        s = qcomp[col].astype(float)
        return {"min": round(float(s.min()), 4), "p25": round(float(s.quantile(0.25)), 4),
                "median": round(float(s.median()), 4), "p75": round(float(s.quantile(0.75)), 4),
                "max": round(float(s.max()), 4)}

    protocol_md = ROOT / "docs" / "protocols" / "cm5_mri_eligibility.md"
    frozen_protocol = ROOT / "docs" / "protocol" / "cm5_frozen_protocol.md"
    frozen_seal = ROOT / "data" / "manifests" / "cm5_protocol_seal.json"

    seal = {
        "seal_id": "CM5_ELIGIBILITY_SEAL",
        "amendment": cfg["amendment"],
        "outcome_independent": True,
        "attestation": cfg["attestation"],
        "dataset": {"id": c["dataset"], "snapshot": c["snapshot"],
                    "fmriprep": c["fmriprep_version"], "space": c["space"],
                    "tr_s": c["tr_s"], "n_volumes": c["n_volumes"],
                    "scan_duration_s": c["scan_duration_s"]},
        "hrf": {"buffer_s": c["hrf_safe_buffer_s"], "window_s": c["neural_history_window_s"],
                "n_nonsteady_volumes": c["n_nonsteady_volumes"],
                "steady_state_onset_s": c["steady_state_onset_s"],
                "amendment": "AM-1: primary targets require onset >= 36 s (full window steady-state)"},
        "horizons": [1, 3, 5, 10],
        "models": ["M0_behavioral", "M1_neural_only", "M2_behavior_nuisance",
                   "M3_behavior_neural", "M4_behavior_nuisance_neural"],
        "decisive_contrast": "M4_minus_M2",
        "residual_test": "brain -> (true_future - behavioral_prediction)",
        "negative_controls": ["NC1_subject_perm", "NC2_temporal_shift",
                              "NC3_block_perm", "NC4_nuisance_only",
                              "NC5_neural_randomize", "NC6_target_perm"],
        "qc_thresholds_frozen": cfg["criteria"]["D_motion_qc"],
        "min_usable_targets": min_targets,
        "target_rule": cfg["criteria"]["C_temporal"]["target_rule"],
        "post_acquisition_gates": cfg["post_acquisition_gates"],
        "sensitivity_analyses": cfg["sensitivity_analyses"],
        "nuisance_set": cfg["nuisance_set_m2_m4"],
        "counts": {
            "total_dataset_subjects": int(len(final)),
            "eligible": int(len(elig)),
            "excluded": int(len(excl)),
            "split_eligible": split_counts,
            "split_original": {p: len(split_seal["split"][p]) for p in ("train", "val", "test")},
        },
        "included_subjects": {
            p: sorted(elig.loc[elig["cm3_split"] == p, "subject_id"].tolist())
            for p in ("train", "val", "test")
        },
        "excluded_subjects": [
            {"subject": r["subject_id"], "split": r["cm3_split"],
             "reason": r["exclusion_reason"]}
            for _, r in excl.iterrows()
        ],
        "usable_thought_events": {
            "steady_state_target_total": int(elig["steady_state_target_count"].sum()),
            "steady_state_target_min": int(elig["steady_state_target_count"].min()),
            "steady_state_target_median": float(elig["steady_state_target_count"].median()),
            "steady_state_target_max": int(elig["steady_state_target_count"].max()),
        },
        "qc_distribution_snapshot": {
            "n_with_confounds": int(len(qcomp)),
            "fd_mean": qdist("fd_mean"),
            "fd_p95": qdist("fd_p95"),
            "fd_gt05_frac": qdist("fd_gt05_frac"),
            "fd_gt10_frac": qdist("fd_gt10_frac"),
            "fd_gt20_frac": qdist("fd_gt20_frac"),
            "dvars_gt50med_frac": qdist("dvars_gt50med_frac"),
            "n_volumes": {"min": int(qcomp["n_volumes"].min()),
                          "max": int(qcomp["n_volumes"].max())},
        },
        "split_seal_cm2": split_seal["seal"],
        "hashes": {
            "eligibility_config": sha256_file(CONFIG),
            "eligibility_protocol_md": sha256_file(protocol_md),
            "frozen_cm5_protocol_md": sha256_file(frozen_protocol),
            "frozen_cm5_protocol_seal": sha256_file(frozen_seal),
            "metadata_audit_tsv": sha256_file(METADATA),
            "qc_audit_tsv": sha256_file(QC),
            "bold_url_audit_tsv": sha256_file(BOLD_URL),
        },
        "decision": "CM5_COHORT_SEALED",
    }
    SEAL_OUT.write_text(json.dumps(seal, indent=2))
    print(json.dumps(seal["counts"], indent=2))
    print("excluded:")
    for e in seal["excluded_subjects"]:
        print(f"  {e['subject']} ({e['split']}): {e['reason']}")
    print(f"seal sha256: {sha256_file(SEAL_OUT)}")
    print(f"wrote {SEAL_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
