"""Build the normalized derived thought-event representation from OSF a56rm.

For each subject with a sentence-level transcript, group sentences by
`thoughtID` into THOUGHTS (the next-thought unit) and write
data/derived/thought_events/<subject>_thoughts.tsv.

Each thought event carries:
  subject_id, event_id, text, start_time, end_time, duration, topic, category,
  n_sentences, source_file, source_granularity, rating_source
  + the 14 psychological rating dimensions (aggregated from sentences).

Provenance:
  * transcript / start / end / topic / category / thoughtID : directly observed
  * rating dimensions : model-inferred (gpt_generated) for all subjects;
    human_validation available for the 18-subject validation subset.

Writes data/derived/thought_events/_manifest.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

RAW = Path("/home/jovyan/work/causal-mind-v2/data/raw/osf")
OUT = Path("/home/jovyan/work/causal-mind-v2/data/derived/thought_events")
TREE = Path("/home/jovyan/work/causal-mind-v2/data/manifests/osf_a56rm_tree.json")

RATING_DIMS = [
    "Emotional intensity (-4: very negative--0: neutral--4: very positive)",
    "Joy (1: not at all--4: very much)",
    "Sadness (1: not at all--4: very much)",
    "Fear (1: not at all--4: very much)",
    "Anger (1: not at all--4: very much)",
    "Disgust (1: not at all--4: very much)",
    "Surprise (1: not at all--4: very much)",
    "Anxiety (1: not at all--4: very much)",
    "Vision (1: not at all--4: very much)",
    "Audition (1: not at all--4: very much)",
    "Olfaction (1: not at all--4: very much)",
    "Gustation (1: not at all--4: very much)",
    "Somatosensation (1: not at all--4: very much)",
    "Interoception (1: not at all--4: very much)",
]
RATING_SHORT = [
    "emotional_intensity", "joy", "sadness", "fear", "anger", "disgust",
    "surprise", "anxiety", "vision", "audition", "olfaction", "gustation",
    "somatosensation", "interoception",
]


def _sentence_df(sub: str) -> pd.DataFrame:
    p = RAW / f"data/transcripts_and_timestamps/sentence_level/{sub}_transcripts.xlsx"
    return pd.ExcelFile(p).parse("Sheet1")


def _rating_df(sub: str, kind: str) -> pd.DataFrame | None:
    if kind == "gpt":
        p = RAW / f"data/sentence_level_ratings/gpt_generated/{sub}.xlsx"
    else:
        p = RAW / f"data/sentence_level_ratings/human_validation/Rater1/{sub}.xlsx"
    if not p.exists():
        return None
    return pd.ExcelFile(p).parse("Sheet1")


def build_subject(sub: str) -> dict:
    sent = _sentence_df(sub)
    sent = sent.reset_index(drop=True)
    gpt = _rating_df(sub, "gpt")
    human = _rating_df(sub, "human")

    # per-sentence ratings (GPT primary; human for the validation subset)
    rating_source = "none"
    if gpt is not None and len(gpt) == len(sent):
        rating_source = "gpt_generated"
        src = gpt
    elif human is not None and len(human) == len(sent):
        rating_source = "human_validation"
        src = human
    else:
        src = None

    rows = []
    for tid, grp in sent.groupby("thoughtID", sort=True):
        text = " ".join(grp["Transcribed Sentence"].astype(str).str.strip())
        st = float(grp["Start Time"].min())
        en = float(grp["End Time"].max())
        row = {
            "subject_id": sub,
            "event_id": int(tid),
            "text": text,
            "start_time": st,
            "end_time": en,
            "duration": en - st,
            "topic": grp["topic"].iloc[0],
            "category": int(grp["category"].iloc[0]),
            "n_sentences": int(len(grp)),
            "source_file": f"data/transcripts_and_timestamps/sentence_level/{sub}_transcripts.xlsx",
            "source_granularity": "thought",
            "rating_source": rating_source,
        }
        if src is not None:
            idx = grp.index  # sentence row positions
            for full, short in zip(RATING_DIMS, RATING_SHORT, strict=True):
                if full in src.columns:
                    row[short] = float(src.loc[idx, full].astype(float).mean())
        rows.append(row)
    rows.sort(key=lambda r: r["event_id"])
    return {"subject": sub, "rows": rows, "n_thoughts": len(rows),
            "rating_source": rating_source}


def main(subjects: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    for sub in subjects:
        try:
            res = build_subject(sub)
        except FileNotFoundError:
            continue
        pd.DataFrame(res["rows"]).to_csv(OUT / f"{sub}_thoughts.tsv",
                                         sep="\t", index=False)
        manifest.append({"subject": sub, "n_thoughts": res["n_thoughts"],
                         "rating_source": res["rating_source"],
                         "file": f"{sub}_thoughts.tsv"})
        print(f"  {sub}: {res['n_thoughts']} thoughts (ratings={res['rating_source']})")
    (OUT / "_manifest.json").write_text(json.dumps(
        {"n_subjects": len(manifest), "subjects": manifest}, indent=2))
    print(f"wrote {len(manifest)} subject files to {OUT}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:  # all subjects with a sentence transcript
        tree = json.load(TREE.open())
        subs = sorted({f["path"].split("/")[-1].split("_")[0]
                       for f in tree["files"]
                       if f["path"].startswith(
                           "/data/transcripts_and_timestamps/sentence_level/")})
        main(subs)
