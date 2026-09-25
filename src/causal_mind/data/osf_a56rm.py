"""OSF a56rm behavioral loader -- authoritative BEHAVIORAL source for ds006067.

Dual-source dataset model:
  * MRI source      : OpenNeuro ds006067 v2.0.0
  * Behavioral source: OSF project a56rm ("Think aloud behavioral data")

Reads the normalized derived thought events produced by
data/scripts/build_thought_events.py (data/derived/thought_events/).
"""
from __future__ import annotations

import pandas as pd

from causal_mind import paths

DERIVED = paths.thought_events_dir()
RATING_DIMS = (
    "emotional_intensity", "joy", "sadness", "fear", "anger", "disgust",
    "surprise", "anxiety", "vision", "audition", "olfaction", "gustation",
    "somatosensation", "interoception",
)


def load_thought_events(subject: str) -> list[dict]:
    """Load one subject's normalized thought events (in event_id / time order)."""
    df = pd.read_csv(DERIVED / f"{subject}_thoughts.tsv", sep="\t")
    df = df.sort_values("event_id").reset_index(drop=True)
    events: list[dict] = []
    for _, r in df.iterrows():
        ev: dict = {
            "onset": float(r["start_time"]),
            "duration": float(r["duration"]),
            "transcript": str(r["text"]),
            "topic": str(r["topic"]) if pd.notna(r["topic"]) else None,
            "observed_category": int(r["category"]) if pd.notna(r["category"]) else None,
            "rating_source": str(r["rating_source"]),
        }
        ratings: dict[str, float] = {}
        for d in RATING_DIMS:
            if d in df.columns and pd.notna(r[d]):
                ratings[d] = float(r[d])
        ev["ratings"] = ratings
        events.append(ev)
    return events


def all_subjects() -> list[str]:
    """All subjects with a derived thought-event file."""
    return sorted(p.stem.replace("_thoughts", "")
                  for p in DERIVED.glob("*_thoughts.tsv"))
