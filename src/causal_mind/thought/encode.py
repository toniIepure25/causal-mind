"""Frozen text encoders for thought-state embeddings (precomputed + cached).

Two encoders, both treated as FROZEN (no fitting on test data):

* ``MiniLMEncoder`` -- all-MiniLM-L6-v2 (384-d), a pretrained, frozen sentence
  encoder. Captures paraphrase/semantics. No fitting step, so no leakage by
  construction. PRIMARY semantic representation.
* ``TfidfEncoder``  -- lexical bag-of-words (sklearn). MUST be fit on TRAIN
  subjects only (leakage-safe); used as a lexical robustness check, not the
  primary semantic representation.

Embeddings are cached to disk (``data/embeddings/<encoder>/<subject>.npy``) so
long runs are resumable and token-expiry-safe.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

os.environ.setdefault("HF_HOME", "/home/jovyan/work/.hf-home")
os.environ.setdefault("TRANSFORMERS_CACHE", "/home/jovyan/work/.hf-home")

CACHE_DIR = Path("/home/jovyan/work/causal-mind-v2/data/embeddings")


class MiniLMEncoder:
    name = "all-MiniLM-L6-v2"
    dim = 384

    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer

        self._m = SentenceTransformer(self.name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(
            self._m.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True),
            dtype=np.float32,
        )


class TfidfEncoder:
    name = "tfidf"
    dim = None  # set after fit

    def __init__(self, max_features: int = 20000) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer

        self._v = TfidfVectorizer(stop_words="english", max_features=max_features)
        self._fitted = False

    def fit(self, texts: list[str]) -> TfidfEncoder:
        self._v.fit(list(texts))
        self.dim = self._v.vocabulary_size_
        self._fitted = True
        return self

    def encode(self, texts: list[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("TfidfEncoder must be fit on TRAIN subjects before encode")
        return self._v.transform(list(texts)).toarray().astype(np.float32)


def _cache_path(encoder_name: str, subject: str) -> Path:
    return CACHE_DIR / encoder_name / f"{subject}.npy"


def encode_subject_cached(
    encoder, subject: str, texts: list[str], force: bool = False
) -> np.ndarray:
    """Encode one subject's thoughts, caching the matrix to disk (resumable)."""
    p = _cache_path(encoder.name, subject)
    if not force and p.exists():
        arr = np.load(p)
        if arr.shape[0] == len(texts):
            return arr
    arr = encoder.encode(texts)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.save(p, arr)
    return arr
