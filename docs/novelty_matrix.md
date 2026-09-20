# CAUSAL MIND — Novelty Matrix

What is novel, what is standard, and what is borrowed. Honest positioning against prior
work. Part of the `cm8-prehuman-v1.0` freeze.

## The three contributions and their novelty

### Contribution 1 — Multi-horizon semantic forecasting of the thought stream (Paper 1)

| aspect | status |
| --- | --- |
| Predicting the *next* thought's semantics from recent history | **Novel application** (thought diaries + frozen embeddings + multi-horizon heads). Sequence prediction over text is standard; applying it to *spontaneous thought semantics* with a sealed subject-disjoint protocol is new. |
| Multi-horizon (h=1..10) with a smooth decay of the gain | **Novel result** (the decay shape is the qualitative claim). Multi-horizon forecasting is a standard technique; the *thought-stream* result and its horizon (TPH ≥ ~10 thoughts) are new. |
| Thought Predictive Horizon (TPH) as a quantity | **Novel framing** (a finite, measurable predictive horizon for spontaneous thought). |
| Baselines B0–B7 + permutation nulls | **Standard** (n-gram, Markov, retrieval, persistence) — included to make the claim honest. |

**Net:** the *method* is simple and standard; the *result* (a real, finite, forecastable
semantic signal in spontaneous thought, with a measurable horizon) is the contribution.

### Contribution 2 — A validated causal-inference method + a frozen confirmatory design (Paper 2)

| aspect | status |
| --- | --- |
| Showing the observational thought stream is **not** causally identifiable (0/84 edges) | **Novel negative result** (a full identifiability audit on the thought stream). |
| A counterfactual engine that **refuses** to label an unidentified counterfactual causal | **Novel enforcement** (the refusal is in code, not just prose). |
| Validating the method on an independent public dataset (ds005494) before the real question | **Novel practice** (method validation as a bridge, FORECAST → INTERVENE). |
| The predicted-future-basin (BRP) estimand | **Novel estimand** (P(future leaves the frozen predicted basin \| intervention)). |
| A **frozen, pre-human-hardened** confirmatory design (10/10 gates) | **Novel rigor** (the design is frozen and pre-validated before any human data). |
| Subject-clustered permutation, bootstrap CIs | **Standard** (well-established causal-inference tools). |

**Net:** the *tools* are standard; the *bridge* (prediction → validated causal method →
frozen confirmatory design for a question no public dataset answers) is the contribution.

### Contribution 3 — The synthetic Oracle lab (CM-9A → CM-9)

| aspect | status |
| --- | --- |
| A synthetic world with 4 oracle conditions × 11 agent policies | **Novel construction** (a controllable world to study prediction vs. intervention). |
| RPR / PIE metrics for self-prediction under intervention | **Novel metrics** (Relative Prediction Ratio, Prediction–Intervention Effect). |
 | Computational-irreducibility (O10) + game-theoretic best-response (O7) probes | **Novel probes** (limits of detectability). |

**Net:** a synthetic theory of *when an oracle's intervention is detectable* in an agent's
self-prediction. Synthetic only; no real-human claim.

## What is explicitly NOT novel (to avoid overclaiming)

- The sentence-embedding representation (MiniLM) — borrowed, frozen.
- Ridge regression / multi-horizon heads — standard.
- Permutation tests / bootstrap CIs — standard.
- The public datasets (OSF `a56rm`, ds005494) — borrowed, cited.
- The fMRI null (CM-5) — a *negative* result; the null is the contribution, not a new method.

## The gap the program fills

**No public dataset tests voluntary redirection of a predicted thought (E8).** The closest
public datasets test open-loop stimulation (ds005494) or affect transitions (ds006583), not
the voluntary redirection of a *predicted* semantic trajectory. That gap is exactly what the
frozen CM-8 confirmatory experiment is designed to fill — and it is why the confirmatory
step must be an own experiment, not an analysis of public data.
