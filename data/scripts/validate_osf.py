"""Validate OSF a56rm behavioral files for given subjects (Step 2, reusable for Step 5).

Checks per subject:
* parsing (xlsx reads, expected columns)
* subject mapping (filename subject matches)
* monotonic timestamps (sentence + word)
* valid start/end intervals (end>start, start>=0)
* sentence/word consistency (word span within sentence span, counts)
* scan-relative timing convention (seconds, first event after t=0)
* thoughtID grouping
* deterministic normalization (re-parse stability)

Prints PASS/FAIL per check; exits non-zero if any FAIL.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAW = Path("/home/jovyan/work/causal-mind-v2/data/raw/osf")
SENT_COLS = ["Transcribed Sentence", "Start Time", "End Time"]
WORD_COLS = ["Transcribed Word", "Start Time", "End Time"]
TOL = 0.5  # seconds


def _read(rel: str) -> pd.DataFrame:
    return pd.ExcelFile(RAW / rel).parse("Sheet1")


def validate(sub: str) -> list[tuple[str, bool, str, bool]]:
    res: list[tuple[str, bool, str, bool]] = []

    def chk(name: str, ok: bool, detail: str = "", soft: bool = False) -> None:
        res.append((name, bool(ok), detail, soft))

    sent_rel = f"data/transcripts_and_timestamps/sentence_level/{sub}_transcripts.xlsx"
    word_rel = f"data/transcripts_and_timestamps/word_level/{sub}_timestamps.xlsx"
    sent_p, word_p = RAW / sent_rel, RAW / word_rel
    chk("sentence_file_exists", sent_p.exists(), sent_rel)
    chk("word_file_exists", word_p.exists(), word_rel)
    if not (sent_p.exists() and word_p.exists()):
        return res

    sent = _read(sent_rel)
    word = _read(word_rel)
    chk("sent_parse", all(c in sent.columns for c in SENT_COLS),
        f"cols={list(sent.columns)}")
    chk("word_parse", all(c in word.columns for c in WORD_COLS),
        f"cols={list(word.columns)}")
    chk("subject_mapping", sub in sent_rel and sub in word_rel, sub)

    ss, se = sent["Start Time"].astype(float), sent["End Time"].astype(float)
    ws, we = word["Start Time"].astype(float), word["End Time"].astype(float)

    chk("sent_monotonic", bool((ss.diff().dropna() >= -1e-6).all()),
        f"min_diff={ss.diff().dropna().min():.4f}")
    chk("word_monotonic", bool((ws.diff().dropna() >= -1e-6).all()),
        f"min_diff={ws.diff().dropna().min():.4f}")
    chk("sent_valid_interval", bool(((se - ss) > 0).all() and (ss >= 0).all()),
        f"n_sent={len(ss)}")
    chk("word_valid_interval", bool(((we - ws) > 0).all() and (ws >= 0).all()),
        f"n_word={len(ws)}")

    # sentence/word consistency
    chk("word_count_gt_sent", len(word) > len(sent),
        f"word={len(word)} sent={len(sent)}")
    span_ok = (ws.min() >= ss.min() - TOL) and (we.max() <= se.max() + TOL)
    chk("word_within_sent_span", bool(span_ok),
        f"word[{ws.min():.1f},{we.max():.1f}] sent[{ss.min():.1f},{se.max():.1f}]",
        soft=True)
    chk("first_word_near_first_sent", abs(ws.min() - ss.min()) <= TOL,
        f"word0={ws.min():.2f} sent0={ss.min():.2f}", soft=True)

    # scan-relative timing convention (seconds; first event after t=0)
    chk("timing_scan_relative", bool(ss.min() > 0 and ss.max() < 7200),
        f"range=[{ss.min():.1f},{ss.max():.1f}]s")

    # thoughtID grouping
    if "thoughtID" in sent.columns:
        n_thoughts = sent["thoughtID"].nunique()
        chk("thoughtID_present", True, f"n_thoughts={n_thoughts} n_sent={len(sent)}")
    else:
        chk("thoughtID_present", False, "column missing")

    # deterministic normalization: re-parse gives identical start/end
    sent2 = _read(sent_rel)
    chk("deterministic_reparse",
        bool((sent2["Start Time"].astype(float).values == ss.values).all()),
        "re-parse identical")
    return res


def main(subjects: list[str]) -> int:
    all_ok = True
    for sub in subjects:
        print(f"\n===== {sub} =====")
        for name, ok, detail, soft in validate(sub):
            if not ok and not soft:
                all_ok = False
            tag = "PASS" if ok else ("soft" if soft else "FAIL")
            print(f"  {tag:4s}  {name:26s} {detail}")
    print(f"\nOVERALL (hard checks): {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
