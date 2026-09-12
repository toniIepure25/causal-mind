"""ThoughtStateV1 -- the first CAUSAL MIND thought-state representation.

Dual-source provenance (CM-2A, OSF pivot):
  * MRI source       : OpenNeuro ds006067 v2.0.0 (neuroimaging only)
  * Behavioral source: OSF project a56rm (transcripts, timestamps, ratings)

Field provenance:
* DIRECTLY OBSERVED  : transcript, onset, duration, topic (prompt),
                       observed_category (OSF 1-5)
* DERIVED (deterministic, no future info): offset, n_words, n_chars
* MODEL INFERRED     : semantic embedding (frozen MiniLM), coarse category
                       (K-means on the embedding, fit on TRAIN subjects only)
* MODEL INFERRED (GPT): the 14 sentence-level psychological ratings
                       (8 emotion + 6 sensory/modal), aggregated per thought.
                       Validated against human raters on an 18-subject subset.

Model-inferred fields are NEVER treated as ground truth; they are clearly
labeled and kept separate from the directly-observed transcript.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

# The 14 GPT-rated psychological dimensions (model-inferred).
RATING_DIMS = (
    "emotional_intensity", "joy", "sadness", "fear", "anger", "disgust",
    "surprise", "anxiety", "vision", "audition", "olfaction", "gustation",
    "somatosensation", "interoception",
)

# Provenance class for every ThoughtStateV1 field.
PROVENANCE: dict[str, str] = {
    # directly observed (OSF a56rm sentence-level transcript)
    "transcript": "directly_observed",
    "onset": "directly_observed",
    "duration": "directly_observed",
    "topic": "directly_observed",            # the prompt the subject thought about
    "observed_category": "directly_observed",  # OSF category (1-5)
    # derived (deterministic, no future info)
    "offset": "derived_deterministic",
    "n_words": "derived_deterministic",
    "n_chars": "derived_deterministic",
    # model inferred
    "embedding": "model_inferred",           # frozen MiniLM, no fitting
    "category": "model_inferred",            # K-means on embedding, fit on train only
}
# The 14 GPT-rated dimensions are model-inferred (GPT-generated); the
# 18-subject validation subset has human raters cross-checking them.
for _d in RATING_DIMS:
    PROVENANCE[_d] = "model_inferred_gpt"

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
    topic: str | None = None
    observed_category: int | None = None
    ratings: dict[str, float] = field(default_factory=dict)
    offset: float = field(init=False)
    n_words: int = field(init=False)
    n_chars: int = field(init=False)
    embedding: np.ndarray | None = None
    category: int | None = None

    def __post_init__(self) -> None:
        self.offset = self.onset + self.duration
        self.n_words = len(self.transcript.split())
        self.n_chars = len(self.transcript)


def _get(ev, key: str, default=None):
    if isinstance(ev, dict):
        return ev.get(key, default)
    return getattr(ev, key, default)


def states_from_events(subject: str, events: list) -> list[ThoughtState]:
    """Build ThoughtState objects from loader events (no embeddings yet).

    ``events`` is a list of dicts or objects with onset/duration/transcript
    (and optionally topic/observed_category/ratings), in time order.
    """
    out: list[ThoughtState] = []
    for i, ev in enumerate(events):
        out.append(
            ThoughtState(
                subject=subject,
                index=i,
                onset=float(_get(ev, "onset")),
                duration=float(_get(ev, "duration")),
                transcript=str(_get(ev, "transcript")),
                topic=_get(ev, "topic"),
                observed_category=_get(ev, "observed_category"),
                ratings=dict(_get(ev, "ratings", {}) or {}),
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
