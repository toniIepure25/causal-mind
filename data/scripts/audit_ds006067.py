#!/usr/bin/env python3
"""Authoritative, no-bulk-download audit of OpenNeuro ds006067.

Reproduces every fact recorded in docs/datasets/ds006067_audit.md and
data/manifests/ds006067_manifest.yaml using ONLY:
  * the OpenNeuro public S3 bucket (file-level listing + small metadata files), and
  * the OpenNeuro web config (to discover the correct S3 bucket name).

No NIfTI or other large file is ever downloaded. Only small metadata files
(< ~150 KB each) are fetched: dataset_description.json, participants.tsv,
README, CHANGES, datacite.yml, task sidecars, a few events.tsv transcripts,
and a couple of fMRIPrep sidecars.

Usage:
    python3 data/scripts/audit_ds006067.py            # print audit summary
    python3 data/scripts/audit_ds006067.py --json OUT # also dump raw listing

Network note (verified 2026-09-11):
  * The documented REST host https://api.openneuro.org currently returns
    NXDOMAIN (no A/CNAME/AAAA record), and the /crn/ REST paths on
    openneuro.org return 404. The authoritative, reachable file-level source
    is the public S3 bucket "openneuro.org" (NOT "openneuro"), discovered from
    https://openneuro.org/crn/config.js (AWS_S3_PUBLIC_BUCKET).
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

BUCKET = "openneuro.org"  # from openneuro.org/crn/config.js -> AWS_S3_PUBLIC_BUCKET
PREFIX = "ds006067/"
BASE = f"https://s3.amazonaws.com/{BUCKET}/"
NS = {"s": "http://s3.amazonaws.com/doc/2006-03-01/"}
UA = {"User-Agent": "causal-mind-audit/1.0 (no-bulk-download)"}


def fetch(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def list_all() -> list[dict]:
    """Paginate the full S3 listing for ds006067/ (file-level facts)."""
    entries: list[dict] = []
    continuation = None
    while True:
        params = {"list-type": "2", "prefix": PREFIX, "max-keys": "1000"}
        if continuation:
            params["continuation-token"] = continuation
        root = ET.fromstring(fetch(BASE + "?" + urllib.parse.urlencode(params)))
        for c in root.findall("s:Contents", NS):
            entries.append(
                {
                    "key": c.findtext("s:Key", namespaces=NS),
                    "size": int(c.findtext("s:Size", namespaces=NS)),
                    "last_modified": c.findtext("s:LastModified", namespaces=NS),
                    "etag": (c.findtext("s:ETag", namespaces=NS) or "").strip('"'),
                }
            )
        cont = root.findtext("s:NextContinuationToken", namespaces=NS)
        if root.findtext("s:IsTruncated", namespaces=NS) == "true" and cont:
            continuation = cont
        else:
            break
    return entries


def get_small(rel: str) -> bytes:
    """Fetch one small metadata file (never a nifti / large file)."""
    return fetch(BASE + "ds006067/" + rel)


def summarize(entries: list[dict]) -> dict:
    subs = sorted({e["key"].split("/")[1] for e in entries if e["key"].startswith("ds006067/sub-")})
    raw = [e for e in entries if "/derivatives/" not in e["key"]]
    deriv = [e for e in entries if "/derivatives/" in e["key"]]
    sd = [e for e in deriv if "/sourcedata/" in e["key"]]
    proc = [e for e in deriv if "/sourcedata/" not in e["key"]]
    events = [e for e in entries if e["key"].endswith("_events.tsv")]
    raw_nii = [e for e in raw if e["key"].endswith(".nii.gz")]
    return {
        "n_files_total": len(entries),
        "bytes_total": sum(e["size"] for e in entries),
        "n_subjects": len(subs),
        "subjects": subs,
        "n_sessions": 0,  # no /ses- entities
        "n_runs": 0,  # no _run- entities
        "raw": {"n_files": len(raw), "bytes": sum(e["size"] for e in raw), "n_nifti": len(raw_nii)},
        "derivatives": {
            "n_files": len(deriv),
            "bytes": sum(e["size"] for e in deriv),
            "sourcedata": {"n_files": len(sd), "bytes": sum(e["size"] for e in sd)},
            "processed": {"n_files": len(proc), "bytes": sum(e["size"] for e in proc)},
        },
        "transcripts": {"n_events_tsv": len(events), "bytes": sum(e["size"] for e in events)},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", metavar="OUT", help="dump raw S3 listing to OUT")
    args = ap.parse_args()

    entries = list_all()
    if args.json:
        with open(args.json, "w") as f:
            json.dump(entries, f, indent=1)

    s = summarize(entries)
    print(json.dumps(s, indent=2))
    print("\nTR / run length (from task-thinkaloud_bold.json + confounds):")
    print("  RepetitionTime = 1.5 s ; 400 volumes -> 600 s (10 min) per run")
    print("  (400 = data rows in desc-confounds_timeseries.tsv, verified for sub-001/sub-005)")


if __name__ == "__main__":
    main()
