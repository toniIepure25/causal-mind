"""Fetch OSF a56rm behavioral files for given subjects into data/raw/osf/
(preserving the original OSF path structure). Records SHA-256.

Usage: python fetch_osf.py sub-001 sub-005 ...
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

TREE = Path("/home/jovyan/work/causal-mind-v2/data/manifests/osf_a56rm_tree.json")
RAW = Path("/home/jovyan/work/causal-mind-v2/data/raw/osf")
HEADERS = {"User-Agent": "causal-mind/0.1"}


def download(url: str, dest: Path) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    last: Exception | None = None
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            data = urllib.request.urlopen(req, timeout=120).read()
            dest.write_bytes(data)
            return hashlib.sha256(data).hexdigest()
        except urllib.error.HTTPError as e:
            last = e
            if e.code in (403, 429, 500, 502, 503, 504):
                time.sleep(2.0 * (attempt + 1))
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = e
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f"download failed after retries: {url} ({last})")


def main(subjects: list[str]) -> None:
    tree = json.load(TREE.open())
    fetch_all = "all" in subjects
    manifest: list[dict] = []
    for f in tree["files"]:
        if not fetch_all and not any(s in f["path"] for s in subjects):
            continue
        url = (f.get("download") or "").rstrip("/")
        dest = RAW / f["path"].lstrip("/")
        if dest.exists():
            h = hashlib.sha256(dest.read_bytes()).hexdigest()
            tag = "cached"
        else:
            h = download(url, dest)
            tag = "fetched"
        manifest.append({"path": f["path"], "sha256": h, "size": dest.stat().st_size})
        print(f"  {tag:6s} {h[:12]}  {f['path']}  ({dest.stat().st_size} B)")
        if tag == "fetched":
            time.sleep(0.2)
    (RAW / "_osf_fetch_manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"fetched {len(manifest)} files for {subjects}")


if __name__ == "__main__":
    main(sys.argv[1:])
