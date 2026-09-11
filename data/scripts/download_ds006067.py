#!/usr/bin/env python3
"""Reproducible minimal-subset downloader for OpenNeuro ds006067 (ThinkAloud).

Fetches the SMALLEST subset sufficient to validate BIDS structure, transcript
parsing, timestamp alignment, fMRI + derivative loading, and thought-event
construction. Idempotent and resumable (skips files already present with the
expected size; downloads to .part then renames). No bulk / full-dataset fetch.

Source: OpenNeuro public S3 bucket "openneuro.org", prefix "ds006067/" (pinned v2.0.0).
See data/manifests/ds006067_manifest.yaml and docs/datasets/ds006067_audit.md.

Usage:
    python3 data/scripts/download_ds006067.py
    python3 data/scripts/download_ds006067.py --subjects sub-001 sub-005 --dest /path
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request

BUCKET = "openneuro.org"
BASE = f"https://s3.amazonaws.com/{BUCKET}/ds006067/"
UA = {"User-Agent": "causal-mind-ds006067/1.0"}

# Per-subject files (relative to ds006067/). {sub} = full subject token (e.g. "sub-001").
PER_SUBJECT = [
    "{sub}/func/{sub}_task-thinkaloud_events.tsv",
    "derivatives/{sub}/func/{sub}_task-thinkaloud_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz",
    "derivatives/{sub}/func/{sub}_task-thinkaloud_desc-confounds_timeseries.tsv",
    "derivatives/{sub}/anat/{sub}_desc-preproc_T1w.nii.gz",
]
GLOBAL = [
    "participants.tsv",
    "dataset_description.json",
    "task-thinkaloud_bold.json",
]


def sha256_of(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def head_size(url: str) -> int | None:
    try:
        req = urllib.request.Request(url, method="HEAD", headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            return int(r.headers.get("Content-Length", -1))
    except Exception:
        return None


def download(url: str, dest) -> None:
    part = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=600) as r, open(part, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    part.replace(dest)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--subjects", nargs="+", default=["sub-001", "sub-005"])
    ap.add_argument("--dest", default="/home/jovyan/work/causal-mind-v2/data/raw/ds006067")
    ap.add_argument("--no-derivatives", action="store_true",
                    help="fetch only transcripts + global metadata (no NIfTI)")
    args = ap.parse_args()

    import pathlib
    dest = pathlib.Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    rels = list(GLOBAL)
    for sub in args.subjects:
        for pat in PER_SUBJECT:
            if args.no_derivatives and "derivatives/" in pat:
                continue
            rels.append(pat.format(sub=sub))

    print(f"dest={dest}")
    print(f"files to fetch: {len(rels)}")
    t0 = time.time()
    fetched = []
    total_bytes = 0
    for rel in rels:
        url = BASE + rel
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        expected = head_size(url)
        if target.exists() and (expected is None or target.stat().st_size == expected):
            status = "skip (present)"
            size = target.stat().st_size
        else:
            print(f"  GET {rel} ({expected} bytes)", flush=True)
            download(url, target)
            size = target.stat().st_size
            status = "downloaded"
        total_bytes += size
        fetched.append({
            "path": rel,
            "url": url,
            "size": size,
            "sha256": sha256_of(target),
            "status": status,
        })
        print(f"    {status}: {rel} {size} bytes sha256={fetched[-1]['sha256'][:16]}...", flush=True)

    wall = time.time() - t0
    summary = {
        "dataset_id": "ds006067",
        "version": "v2.0.0",
        "bucket": BUCKET,
        "dest": str(dest),
        "subjects": args.subjects,
        "n_files": len(fetched),
        "total_bytes": total_bytes,
        "wall_time_s": round(wall, 1),
        "files": fetched,
    }
    out = dest / "_download_manifest.json"
    out.write_text(json.dumps(summary, indent=2))
    print(f"\nDONE: {len(fetched)} files, {total_bytes/1e6:.1f} MB in {wall:.1f} s -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
