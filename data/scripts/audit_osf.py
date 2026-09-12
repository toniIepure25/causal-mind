"""Audit the OSF a56rm behavioral project (Step 1) via the Waterbutler files API.

Navigates folders through each folder's `links.move` URL. Writes
data/manifests/osf_a56rm_tree.json and prints a summary.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

ROOT_URL = "https://files.osf.io/v1/resources/a56rm/providers/osfstorage/"
HEADERS = {"User-Agent": "causal-mind/0.1"}
OUT = Path("/home/jovyan/work/causal-mind-v2/data/manifests/osf_a56rm_tree.json")


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    return json.load(urllib.request.urlopen(req, timeout=60))


def main() -> None:
    files: list[dict] = []
    folders: list[dict] = []
    visited: set[str] = set()

    def walk(url: str, depth: int = 0) -> None:
        fid = url.rstrip("/").rsplit("/", 1)[-1]
        if fid in visited:
            print(f"  [skip visited] {fid}")
            return
        visited.add(fid)
        r = get(url)
        for e in r["data"]:
            a = e["attributes"]
            kind = a.get("kind")
            mat = a.get("materialized") or ""
            print(f"{'  '*depth}{kind:6s} {mat}  ({a.get('size') or 0} B)")
            if kind == "folder":
                folders.append({"path": mat, "id": e["id"]})
                move = (e.get("links", {}) or {}).get("move")
                if move:
                    walk(move, depth + 1)
            elif kind == "file":
                files.append({
                    "path": mat,
                    "name": a.get("name"),
                    "size": a.get("size") or a.get("sizeInt"),
                    "download": (e.get("links", {}) or {}).get("download")
                                 or (e.get("links", {}) or {}).get("info"),
                })

    t0 = time.time()
    walk(ROOT_URL)
    word = [f for f in files if "/word_level/" in f["path"]]
    sent = [f for f in files if "/sentence_level/" in f["path"]]

    def subjects(fs):
        return sorted({(f["name"] or "").split("_")[0] for f in fs})

    report = {
        "project": {"id": "a56rm", "title": "Think aloud behavioral data"},
        "n_files": len(files), "n_folders": len(folders),
        "total_bytes": sum(f["size"] or 0 for f in files),
        "word_level": {"count": len(word), "subjects": subjects(word)},
        "sentence_level": {"count": len(sent), "subjects": subjects(sent)},
        "folders": folders, "files": files,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))
    print(f"\nDONE in {time.time()-t0:.0f}s | files={len(files)} folders={len(folders)} "
          f"total={report['total_bytes']/1e6:.1f} MB")
    print(f"word_level={len(word)} (subj {len(subjects(word))}) | "
          f"sentence_level={len(sent)} (subj {len(subjects(sent))})")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
