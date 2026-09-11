"""Tests for the CM-2 pipeline (ThoughtStateV1, prospective, protocol, baselines,
models, analyses). Uses a fast deterministic mock encoder for logic tests so the
suite is offline-robust; one integration test exercises the real MiniLM encoder.

Runs against the 2 local subjects (sub-001, sub-005); skips cleanly if absent.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from causal_mind.data import ds006067 as L
from causal_mind.eval import analyses, protocol
from causal_mind.forecast import baselines, models
from causal_mind.thought import prospective, state_v1

DATA = L.DEFAULT_DATA_ROOT
SUBS = ["sub-001", "sub-005"]
pytestmark = pytest.mark.skipif(
    not (DATA / "participants.tsv").exists()
    or not (DATA / "sub-001" / "func" / "sub-001_task-thinkaloud_events.tsv").exists(),
    reason="ds006067 minimal subset not present",
)


class MockEncoder:
    """Deterministic, offline, small-dim encoder (logic tests only)."""

    name = "mock"
    dim = 16

    def encode(self, texts: list[str]) -> np.ndarray:
        out = []
        for t in texts:
            v = np.zeros(16)
            for w in t.lower().split():
                v[int(hashlib.md5(w.encode()).hexdigest(), 16) % 16] += 1
            n = np.linalg.norm(v)
            out.append(v / n if n > 0 else v)
        return np.asarray(out, dtype=np.float32)


@pytest.fixture(scope="module")
def states_by_sub() -> dict:
    enc = MockEncoder()
    out = {}
    for s in SUBS:
        st = state_v1.states_from_events(s, L.load_events(s))
        state_v1.embed_states(st, enc)
        out[s] = st
    return out


@pytest.fixture(scope="module")
def corpus(states_by_sub) -> baselines.TrainCorpus:
    train = states_by_sub["sub-001"]
    km = state_v1.fit_categories(train, n_clusters=4)
    for s in SUBS:
        state_v1.assign_categories(states_by_sub[s], km)
    return baselines.TrainCorpus.build(train, n_clusters=4)


# --- ThoughtStateV1 -------------------------------------------------------- #
def test_provenance_covers_all_fields():
    for f in ("transcript", "onset", "duration", "offset", "n_words", "n_chars",
              "embedding", "category"):
        assert f in state_v1.PROVENANCE
    assert state_v1.PROVENANCE["transcript"] == "directly_observed"
    assert state_v1.PROVENANCE["embedding"] == "model_inferred"
    assert state_v1.PROVENANCE["category"] == "model_inferred"
    for unavailable in ("temporality", "affect_valence", "social_content"):
        assert state_v1.PROVENANCE[unavailable] == "unavailable"


def test_feature_fields_exclude_future():
    # no feature may depend on t+1 or later
    assert "embedding" in state_v1.FEATURE_FIELDS
    assert not any("next" in f or "gap" in f for f in state_v1.FEATURE_FIELDS)


def test_state_derived_fields(states_by_sub):
    st = states_by_sub["sub-001"][0]
    assert st.offset == pytest.approx(st.onset + st.duration)
    assert st.n_words == len(st.transcript.split())
    assert st.n_chars == len(st.transcript)


# --- prospective ----------------------------------------------------------- #
def test_prospective_leakage_free(states_by_sub):
    for s in SUBS:
        for k in (1, 2, 3):
            samples = prospective.build_prospective_samples(states_by_sub[s], k=k)
            prospective.all_samples_leakage_free(samples, states_by_sub)
            assert all(sm.is_prospective for sm in samples)


def test_prospective_history_strictly_past(states_by_sub):
    samples = prospective.build_prospective_samples(states_by_sub["sub-005"], k=3)
    for sm in samples:
        assert max(sm.history) < sm.target_index
        assert len(sm.history) == 3


# --- protocol -------------------------------------------------------------- #
def test_split_disjoint_and_complete(states_by_sub):
    subjects = list(states_by_sub.keys()) + [f"sub-{i:03d}" for i in range(6, 40)]
    split = protocol.subject_disjoint_split(subjects, seed=20260911)
    allc = set(split.train) | set(split.val) | set(split.test)
    assert allc == set(subjects)
    assert not (set(split.train) & set(split.val))
    assert not (set(split.train) & set(split.test))
    assert not (set(split.val) & set(split.test))


def test_split_seal_stable_and_detects_change(tmp_path, monkeypatch):
    monkeypatch.setattr(protocol, "SEAL_PATH", tmp_path / "seal.json")
    subjects = [f"sub-{i:03d}" for i in range(20)]
    s1 = protocol.subject_disjoint_split(subjects, seed=1)
    h1 = protocol.seal_split(s1, seed=1, n_subjects=20)
    assert protocol.verify_seal(s1, seed=1, n_subjects=20)
    s2 = protocol.subject_disjoint_split(subjects, seed=2)
    assert protocol.seal_split(s2, seed=2, n_subjects=20) != h1


def test_metrics_basics():
    a = np.array([1.0, 0.0, 0.0])
    assert protocol.cosine(a, a) == pytest.approx(1.0)
    assert protocol.cosine(a, np.array([0.0, 1.0, 0.0])) == pytest.approx(0.0)
    cands = [a, np.array([0.2, 0.9, 0.0]), np.array([0.0, 0.0, 1.0])]
    assert protocol.retrieval_rank(a, cands) == 1


def test_bootstrap_ci_contains_mean():
    v = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    mean, lo, hi = protocol.bootstrap_ci(v, n_boot=200, seed=0)
    assert lo <= mean <= hi
    assert lo < 3.0 < hi


# --- baselines ------------------------------------------------------------- #
def test_all_baselines_produce_predictions(states_by_sub, corpus):
    st = states_by_sub["sub-005"]
    samples = prospective.build_prospective_samples(st, k=2)
    for _fn_name, fn in baselines.BASELINES.items():
        pred = fn(samples[0], st, corpus)
        assert isinstance(pred, baselines.Prediction)
        assert pred.embedding is not None and pred.embedding.shape == st[0].embedding.shape


def test_corpus_only_train_subjects(states_by_sub, corpus):
    # the train corpus must not contain the test subject's embeddings
    test_emb = states_by_sub["sub-005"][0].embedding
    assert not np.any(np.isclose(corpus.emb_all, test_emb, atol=1e-6).all(axis=1))


# --- models ---------------------------------------------------------------- #
def test_linear_transition_fit_predict(states_by_sub, corpus):
    train = states_by_sub["sub-001"]
    samples = prospective.build_prospective_samples(train, k=1)
    X, Y = models.build_xy(samples, states_by_sub)
    m = models.LinearTransition(k=1, alpha=10.0).fit(X, Y)
    st = states_by_sub["sub-005"]
    pred = m.predict(prospective.build_prospective_samples(st, k=1)[0], st)
    assert pred.shape == st[0].embedding.shape
    assert m.param_count() > 0


def test_gru_next_if_torch(states_by_sub):
    pytest.importorskip("torch")
    train = states_by_sub["sub-001"]
    samples = prospective.build_prospective_samples(train, k=2)
    X, Y = models.build_xy(samples, states_by_sub)
    m = models.GRUNext(k=2, dim=16, hidden=8, layers=1, epochs=2, batch=32).fit(X, Y)
    st = states_by_sub["sub-005"]
    pred = m.predict(prospective.build_prospective_samples(st, k=2)[0], st)
    assert pred.shape == (16,)


# --- analyses -------------------------------------------------------------- #
def test_analyses_return_expected_keys(states_by_sub, corpus):
    test_subs = ["sub-005"]
    train = states_by_sub["sub-001"]
    X, Y = models.build_xy(prospective.build_prospective_samples(train, k=1), states_by_sub)
    lt = models.LinearTransition(k=1, alpha=10.0).fit(X, Y)
    pred = analyses.model_as_predictor(lt)

    imm = analyses.immediate_predictability(
        baselines.b0_marginal, baselines.b1_previous_state, states_by_sub, test_subs, 1, corpus)
    assert "B0_marginal" in imm and "B1_previous_state" in imm and "delta" in imm

    sv = analyses.semantic_vs_categorical(pred, states_by_sub, test_subs, 1, corpus)
    assert "semantic_cosine" in sv

    cs = analyses.cross_subject(pred, states_by_sub, test_subs, 1, corpus)
    assert cs["n_test_subjects"] == 1

    def fit_fn(k: int):
        Xk, Yk = models.build_xy(
            prospective.build_prospective_samples(states_by_sub["sub-001"], k=k), states_by_sub)
        return analyses.model_as_predictor(models.LinearTransition(k=k, alpha=10.0).fit(Xk, Yk))

    curve = analyses.history_depth_curve(
        fit_fn, states_by_sub, test_subs, corpus, ks=(1, 2), seed=0)
    assert 1 in curve and 2 in curve

    pn = analyses.permutation_null(pred, states_by_sub, test_subs, 1, corpus, n_null=20, seed=0)
    assert "observed" in pn and "p_value" in pn and 0.0 <= pn["p_value"] <= 1.0


# --- integration: real MiniLM encoder (skip if unavailable) ---------------- #
def test_minilm_encoder_integration():
    pytest.importorskip("sentence_transformers")
    from causal_mind.thought import encode

    enc = encode.MiniLMEncoder()
    v = enc.encode(["I am thinking about my mother", "the scanner is very noisy"])
    assert v.shape == (2, 384)
    sim = protocol.cosine(v[0], v[1])
    assert -1.0 <= sim <= 1.0
