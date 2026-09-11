#!/usr/bin/env python3
"""Robust, resumable fetch of ALL ds006067 transcripts (events.tsv) + participants.tsv.

CM-2 (non-neural) only needs the transcripts, which are tiny (~2 MB total for 118
subjects). OpenNeuro S3 is intermittently 404ing, so this retries aggressively and
runs for a long time (up to ~3 h) until every file is valid, then writes a manifest.

Resumable: skips files already present and valid. Writes:
  data/raw/ds006067/participants.tsv
  data/raw/ds006067/sub-XXX/func/sub-XXX_task-thinkaloud_events.tsv
  data/raw/ds006067/_cm2_fetch_manifest.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2/data/raw/ds006067")
BASE = "https://s3.amazonaws.com/openneuro.org/ds006067/v2.0.0"
MAX_WALL_S = 3 * 3600
LOG = Path("/tmp/cm2-fetch.log")


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    print(line, flush=True)
    try:
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception:
        pass


def fetch(url: str, tries: int = 8, base_wait: float = 3.0) -> bytes | None:
    for i in range(tries):
        try:
            return urllib.request.urlopen(url, timeout=30).read()
        except Exception as e:  # noqa: BLE001
            wait = base_wait * (i + 1)
            log(f"  retry {i + 1}/{tries} {url.split('/')[-1]}: {type(e).__name__} (wait {wait:.0f}s)")
            time.sleep(wait)
    return None


def valid_participants(txt: str) -> bool:
    first = txt.strip().split("\n", 1)[0]
    return first.startswith("participant_id") and "\t" in first


def valid_events(txt: str) -> bool:
    first = txt.strip().split("\n", 1)[0]
    return first.startswith("onset") and "duration" in first and "transcript" in first


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    t0 = time.time()
    log("=== CM-2 transcript fetch start ===")
    # 1) participants.tsv
    part_path = ROOT / "participants.tsv"
    part_txt = None
    while time.time() - t0 < MAX_WALL_S:
        if part_path.exists() and valid_participants(part_path.read_text(errors="replace")):
            part_txt = part_path.read_text()
            log("participants.tsv already valid")
            break
        b = fetch(f"{BASE}/participants.tsv")
        if b is not None and valid_participants(b.decode(errors="replace")):
            part_path.write_bytes(b)
            part_txt = b.decode()
            log(f"fetched participants.tsv ({len(b)} bytes)")
            break
        log("participants.tsv not ready; sleeping 60s (S3 likely down)")
        time.sleep(60)
    if part_txt is None:
        log("FATAL: could not fetch participants.tsv within wall limit")
        return 1

    subjects = [ln.split("\t")[0] for ln in part_txt.strip().split("\n")[1:] if ln.strip()]
    log(f"subjects: {len(subjects)}")

    manifest = {"dataset": "ds006067", "version": "v2.0.0", "base_url": BASE,
                "participants_sha256": sha(part_path.read_bytes()), "files": {}}
    # load existing manifest if present (resumable)
    mpath = ROOT / "_cm2_fetch_manifest.json"
    if mpath.exists():
        try:
            manifest.update(json.loads(mpath.read_text()))
        except Exception:
            pass

    def ev_path(sub: str) -> Path:
        return ROOT / sub / "func" / f"{sub}_task-thinkaloud_events.tsv"

    def done(sub: str) -> bool:
        p = ev_path(sub)
        return p.exists() and valid_events(p.read_text(errors="replace"))

    pending = [s for s in subjects if not done(s)]
    log(f"pending events.tsv: {len(pending)}/{len(subjects)}")

    while pending and time.time() - t0 < MAX_WALL_S:
        still = []
        for sub in pending:
            if done(sub):
                continue
            url = f"{BASE}/{sub}/func/{sub}_task-thinkaloud_events.tsv"
            b = fetch(url, tries=6, base_wait=2.0)
            if b is not None and valid_events(b.decode(errors="replace")):
                p = ev_path(sub)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b)
                manifest["files"][sub] = {"path": f"{sub}/func/{sub}_task-thinkaloud_events.tsv",
                                          "sha256": sha(b), "bytes": len(b), "url": url}
                log(f"fetched {sub} events.tsv ({len(b)} bytes)")
            else:
                still.append(sub)
        pending = still
        if pending:
            log(f"{len(pending)} still pending; sleeping 45s (S3 likely down)")
            time.sleep(45)

    manifest["fetched"] = len(manifest["files"])
    manifest["total_subjects"] = len(subjects)
    manifest["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    mpath.write_text(json.dumps(manifest, indent=2))
    log(f"=== CM-2 fetch done: {manifest['fetched']}/{len(subjects)} events.tsv ===")
    return 0 if not pending else 2


if __name__ == "__main__":
    sys.exit(main())
