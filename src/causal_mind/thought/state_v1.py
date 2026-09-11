"""ThoughtStateV1 -- the first CAUSAL MIND thought-state representation.

Scientific honesty (CM-2A): ds006067 provides ONLY transcript text + timing
(onset/duration). It has NO psychological annotations (no topic labels, no
word-level timestamps, no affect/temporality/self-relevance/etc.). Therefore:

* DIRECTLY OBSERVED  : transcript, onset, duration
* DERIVED (deterministic, no future info): offset, n_words, n_chars
* MODEL INFERRED     : semantic embedding (frozen MiniLM), coarse category
                       (K-means on the embedding, fit on TRAIN subjects only)
* UNAVAILABLE        : every ground-truth psychological dimension

Model-inferred fields are NEVER treated as ground truth; they are clearly
labeled and kept separate from the directly-observed transcript.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# Provenance class for every ThoughtStateV1 field.
PROVENANCE: dict[str, str] = {
    "transcript": "directly_observed",
    "onset": "directly_observed",
    "duration": "directly_observed",
    "offset": "derived_deterministic",
    "n_words": "derived_deterministic",
    "n_chars": "derived_deterministic",
    "embedding": "model_inferred",          # frozen MiniLM, no fitting
    "category": "model_inferred",           # K-means on embedding, fit on train only
    # Candidate dimensions that are UNAVAILABLE in ds006067 (no annotation):
    "temporality": "unavailable",
    "self_relevance": "unavailable",
    "episodic_past": "unavailable",
    "future_oriented": "unavailable",
    "affect_valence": "unavailable",
    "goal_directedness": "unavailable",
    "social_content": "unavailable",
    "task_relatedness": "unavailable",
}

# Fields safe to use as PREDICTIVE FEATURES for thought t+1 (no future info).
# Note: gap_to_next / boundary-to-next are deliberately EXCLUDED (they use t+1).
FEATURE_FIELDS = ("embedding", "n_words", "onset", "duration")


@dataclass
class ThoughtState:
    subject: str
    index: int
    onset: float
    duration: float
    transcript: str
    offset: float = field(init=False)
    n_words: int = field(init=False)
    n_chars: int = field(init=False)
    embedding: np.ndarray | None = None
    category: int | None = None

    def __post_init__(self) -> None:
        self.offset = self.onset + self.duration
        self.n_words = len(self.transcript.split())
        self.n_chars = len(self.transcript)


def _field(ev, key: str):
    if isinstance(ev, dict):
        return ev[key]
    return getattr(ev, key)


def states_from_events(subject: str, events: list) -> list[ThoughtState]:
    """Build ThoughtState objects from loader events (no embeddings yet).

    ``events`` is a list of dicts or objects with onset/duration/transcript,
    in time order.
    """
    out: list[ThoughtState] = []
    for i, ev in enumerate(events):
        out.append(
            ThoughtState(
                subject=subject,
                index=i,
                onset=float(_field(ev, "onset")),
                duration=float(_field(ev, "duration")),
                transcript=str(_field(ev, "transcript")),
            )
        )
    return out


def embed_states(states: list[ThoughtState], encoder) -> None:
    """Attach frozen embeddings to a list of states (in place)."""
    vecs = encoder.encode([s.transcript for s in states])
    for s, v in zip(states, vecs, strict=True):
        s.embedding = v


def fit_categories(train_states: list[ThoughtState], n_clusters: int = 16, seed: int = 0):
    """Fit a coarse topic model on TRAIN subjects' embeddings only (leakage-safe)."""
    from sklearn.cluster import KMeans

    X = np.vstack([s.embedding for s in train_states if s.embedding is not None])
    km = KMeans(n_clusters=n_clusters, n_init=4, random_state=seed)
    km.fit(X)
    return km


def assign_categories(states: list[ThoughtState], km) -> None:
    """Assign each state the nearest train-fit cluster (in place)."""
    for s in states:
        if s.embedding is not None:
            s.category = int(km.predict(s.embedding.reshape(1, -1))[0])
