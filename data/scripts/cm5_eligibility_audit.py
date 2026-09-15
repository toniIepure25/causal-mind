#!/usr/bin/env python3
"""CM-5 MRI eligibility — metadata-first audit (NO downloads, NO neural outcomes).

Inputs (all on-disk metadata, no content):
  - /home/jovyan/work/ds006067_git          (authoritative metadata mirror of
                                            OpenNeuro ds006067 snapshot 2.0.0:
                                            annex symlinks carry key+size)
  - data/derived/thought_events/            (ThoughtStateV1, frozen CM-2/CM-3)
  - data/manifests/cm2_split_seal.json      (frozen 83/18/17 split)

Output:
  - reports/cm5_subject_eligibility.tsv     (pre-QC eligibility columns)

Eligibility criteria implemented here are OUTCOME-INDEPENDENT (availability,
metadata, temporal compatibility). Motion/QC criteria are applied in a
separate step after cheap confound acquisition and BEFORE any neural
prediction outcome.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")
GIT_CLONE = Path("/home/jovyan/work/ds006067_git")
THOUGHT_EVENTS = ROOT / "data" / "derived" / "thought_events"
SPLIT_SEAL = ROOT / "data" / "manifests" / "cm2_split_seal.json"
OUT = ROOT / "reports" / "cm5_subject_eligibility.tsv"

# Frozen CM-5 protocol constants (data/manifests/cm5_protocol_seal.json)
B_S = 6.0        # HRF-safe buffer
W_S = 15.0       # neural history window
TR_S = 1.5       # repetition time
N_VOLUMES = 400  # dataset-level (CM-1 audit); verified per-subject via confounds later
SCAN_DURATION_S = N_VOLUMES * TR_S  # 600 s
N_NONSTEADY = 10  # fMRIPrep non-steady-state volumes
# AM-1 (CM5-ELIG-1): primary targets require the full neural window in
# steady-state BOLD: onset >= N_NONSTEADY*TR + B + W = 36 s.
ONSET_FROZEN_S = B_S + W_S                        # 21 s (frozen protocol)
ONSET_STEADY_S = N_NONSTEADY * TR_S + B_S + W_S   # 36 s (amendment AM-1)

MNI = "space-MNI152NLin2009cAsym"
REQUIRED_FILES = {
    "bold": f"{{sub}}_task-thinkaloud_{MNI}_desc-preproc_bold.nii.gz",
    "bold_json": f"{{sub}}_task-thinkaloud_{MNI}_desc-preproc_bold.json",
    "mask": f"{{sub}}_task-thinkaloud_{MNI}_desc-brain_mask.nii.gz",
    "confounds": "{sub}_task-thinkaloud_desc-confounds_timeseries.tsv",
    "confounds_json": "{sub}_task-thinkaloud_desc-confounds_timeseries.json",
}
ANNEX_KEY_RE = re.compile(r"SHA256E-s(\d+)--([0-9a-f]{64})")


def annex_info(p: Path) -> tuple[bool, int, str]:
    """Return (present, size_bytes, annex_key_or_empty).

    Handles both git-annex symlink checkouts and plain-text pointer files
    (content like '/annex/objects/SHA256E-s<bytes>--<hash>.<ext>').
    """
    if not p.exists() and not p.is_symlink():
        return False, 0, ""
    if p.is_symlink():
        target = str(p.readlink())
        m = ANNEX_KEY_RE.search(target)
        if not m:
            return True, 0, "UNPARSED"
        return True, int(m.group(1)), f"SHA256E-s{m.group(1)}--{m.group(2)}"
    size = p.stat().st_size
    if size < 1024:
        try:
            content = p.read_text()
            if "/annex/objects/" in content:
                m = ANNEX_KEY_RE.search(content)
                if m:
                    return True, int(m.group(1)), f"SHA256E-s{m.group(1)}--{m.group(2)}"
        except (OSError, UnicodeDecodeError):
            pass
    return True, size, "IN_GIT"


def load_split() -> dict[str, str]:
    seal = json.loads(SPLIT_SEAL.read_text())
    out: dict[str, str] = {}
    for part in ("train", "val", "test"):
        for s in seal["split"][part]:
            out[s] = part
    return out


def load_thoughts(sub: str) -> tuple[bool, int, list[tuple[float, float]]]:
    """Return (available, n_thoughts, [(start_time, duration), ...]).

    Uses the canonical ThoughtStateV1 loader (pandas-based, handles quoted
    fields) so eligibility sees exactly what CM-2/CM-3 saw.
    """
    f = THOUGHT_EVENTS / f"{sub}_thoughts.tsv"
    if not f.exists():
        return False, 0, []
    try:
        from causal_mind.data.osf_a56rm import load_thought_events
        events = load_thought_events(sub)
    except Exception:
        return False, 0, []
    if not events:
        return False, 0, []
    spans = [(e["onset"], e["duration"]) for e in events]
    return True, len(spans), spans


def count_raw_events(sub: str) -> tuple[bool, int]:
    f = GIT_CLONE / sub / "func" / f"{sub}_task-thinkaloud_events.tsv"
    if not f.exists():
        return False, 0
    n = 0
    with f.open() as fh:
        next(fh, None)
        for line in fh:
            if line.strip():
                n += 1
    return n > 0, n


def count_targets(spans: list[tuple[float, float]], onset_min_s: float) -> int:
    """Count target events e with onset >= onset_min_s, ending within scan."""
    return sum(1 for start, dur in spans
               if start >= onset_min_s and start + dur <= SCAN_DURATION_S)


def main() -> int:
    split = load_split()
    subs = sorted(p.name for p in GIT_CLONE.iterdir()
                  if p.is_dir() and re.fullmatch(r"sub-\d{3}", p.name))
    if len(subs) != 118:
        print(f"WARNING: expected 118 subjects, found {len(subs)}", file=sys.stderr)

    cols = [
        "subject_id", "cm3_split",
        "behavioral_available", "n_thoughts",
        "transcript_available", "n_raw_events",
        "bold_available", "bold_size", "bold_annex_key",
        "mask_available", "mask_size", "mask_annex_key",
        "confounds_available", "confounds_size", "confounds_annex_key",
        "bold_json_available", "confounds_json_available",
        "scan_duration_s",
        "hrf_safe_target_count",        # frozen 21 s definition
        "steady_state_target_count",    # AM-1 36 s definition (primary)
        "qc_status", "eligibility_status", "exclusion_reason",
    ]
    rows = []
    for sub in subs:
        dfunc = GIT_CLONE / "derivatives" / sub / "func"
        avail = {}
        sizes = {}
        keys = {}
        for name, tmpl in REQUIRED_FILES.items():
            p = dfunc / tmpl.format(sub=sub)
            avail[name], sizes[name], keys[name] = annex_info(p)

        behav, n_thoughts, spans = load_thoughts(sub)
        transcript, n_raw = count_raw_events(sub)
        n_frozen = count_targets(spans, ONSET_FROZEN_S) if behav else 0
        n_steady = count_targets(spans, ONSET_STEADY_S) if behav else 0

        # Metadata-level availability only (A/B/C criteria). Motion QC (D) is
        # applied by cm5_cohort_seal.py from the confounds QC audit, so this
        # file stays a pure metadata audit.
        reasons = []
        if not behav:
            reasons.append("no_behavioral")
        if not transcript:
            reasons.append("no_transcript")
        if not avail["bold"]:
            reasons.append("no_bold")
        if not avail["mask"]:
            reasons.append("no_mask")
        if not avail["confounds"]:
            reasons.append("no_confounds")
        if not (avail["bold_json"] and avail["confounds_json"]):
            reasons.append("missing_metadata_json")

        if reasons:
            status = "EXCLUDED_METADATA"
        else:
            status = "PENDING_QC"

        rows.append([
            sub, split.get(sub, "UNKNOWN"),
            int(behav), n_thoughts,
            int(transcript), n_raw,
            int(avail["bold"]), sizes["bold"], keys["bold"],
            int(avail["mask"]), sizes["mask"], keys["mask"],
            int(avail["confounds"]), sizes["confounds"], keys["confounds"],
            int(avail["bold_json"]), int(avail["confounds_json"]),
            SCAN_DURATION_S, n_frozen, n_steady,
            "PENDING", status, ";".join(reasons) or "-",
        ])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")

    n_pending = sum(1 for r in rows if r[21] == "PENDING_QC")
    n_excl = len(rows) - n_pending
    print(f"subjects={len(rows)} pending_qc={n_pending} excluded_metadata={n_excl}")
    if n_excl:
        for r in rows:
            if r[21] != "PENDING_QC":
                print(f"  EXCLUDED {r[0]}: {r[22]}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
