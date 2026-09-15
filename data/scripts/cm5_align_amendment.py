#!/usr/bin/env python3
"""Write the CM5-ALIGN-1 alignment-integrity amendment (sub-036 exclusion).

Cohort-level N-GATE 1 verification (reports/cm5_alignment_audit.tsv) found that
sub-036 has 2 OSF thoughts (onsets 4.79s, 65.51s) with no matching raw MRI
events.tsv entry (raw stream starts at 84.13s), so the OSF<->MRI time-base
equality is discrepant for this subject. This is an outcome-independent
data-integrity exclusion (train subject). The 5 subjects with negative first
onsets (pre-scan speech) are ALIGNED (OSF==raw exactly) and KEPT.
"""
import hashlib
import json

ROOT = "/home/jovyan/work/causal-mind-v2"
seal = json.load(open(f"{ROOT}/reports/cm5_cohort_seal.json"))
split = {}
for p in ("train", "val", "test"):
    for s in seal["included_subjects"][p]:
        split[s] = p

amend = {
    "amendment_id": "CM5-ALIGN-1",
    "parent_seal": "CM5_ELIGIBILITY_SEAL",
    "gate": "N-GATE 1 ALIGNMENT (cohort-level post-hoc verification)",
    "rule": "exclude subjects whose OSF thought onsets are not consistent with the "
            "raw MRI events.tsv time base (first-event mismatch > 0.5s or extra "
            "OSF events with no raw counterpart)",
    "outcome_independent": True,
    "can_add_subjects": False,
    "cohort_alignment_audit": {
        "n_subjects": 113,
        "first_event_max_abs_diff_s": 79.34,
        "first_event_mean_abs_diff_s": 0.70,
        "monotonic": "113/113",
        "in_range_0_600s": "108/113",
        "note": "5 subjects (sub-018/083/114/009/086) have negative first onsets "
                "(pre-scan speech) but OSF==raw exactly (diff=0); KEPT.",
    },
    "excluded": [
        {"subject": "sub-036", "split": split["sub-036"],
         "reason": "2 OSF thoughts (4.79s, 65.51s) have no matching raw MRI "
                   "events.tsv entry; raw stream starts at 84.13s",
         "osf_first_starts": [4.79, 65.51, 84.13],
         "raw_first_onsets": [84.13, 90.19, 94.03]},
    ],
    "hashes": {
        "alignment_audit_tsv": hashlib.sha256(
            open(f"{ROOT}/reports/cm5_alignment_audit.tsv", "rb").read()).hexdigest(),
        "parent_cohort_seal": hashlib.sha256(
            open(f"{ROOT}/reports/cm5_cohort_seal.json", "rb").read()).hexdigest(),
    },
}
out = f"{ROOT}/reports/cm5_cohort_amendment_align.json"
json.dump(amend, open(out, "w"), indent=2)
print("excluded:", [e["subject"] for e in amend["excluded"]])
print("amendment sha256:", hashlib.sha256(open(out, "rb").read()).hexdigest())
print("wrote", out)
