# Hypotheses

Status: OPEN | TESTED-PASS | TESTED-FAIL | KILLED
Each hypothesis names the experiment that decides it and the gate it feeds.

## H1 — Next-thought predictability (GATE B)

**Statement.** For ds006067, the next thought event's category (and, secondarily,
semantic content) is predictable from the participant's own thought history above:
B0 (marginal/frequency), B1 (previous category), B2 (first-order Markov),
B3 (semantic nearest-neighbor), B4 (participant-history language model).

**Falsification.** Subject-disjoint evaluation: no model beats B2/B4 by a statistically
significant margin (permutation test, subject-level) on the frozen split.

**Experiments.** CM-3 baseline battery, then simple sequence models (n-gram, RNN/GRU,
transformer if justified).

## H2 — Multi-step futures and the Thought Predictive Horizon (GATE D)

**Statement.** At least one cognitive dimension (topic, temporal orientation, valence,
self-relevance, or category) remains predictable above baseline at horizon H >= 2.

**Falsification.** All dimensions decay to baseline by H=2 under the frozen protocol.

**Experiments.** CM-4 multi-step evaluation with per-dimension skill curves.

## H3 — Neural incremental prospective information (GATE E)

**Statement.** After lag-aware alignment for BOLD hemodynamics, neural features at `t`
improve out-of-sample prediction of `T_{t+1..t+H}` beyond the best language-only model,
on subject-disjoint splits.

**Falsification.** The fusion model does not beat the language-only model (subject-level
bootstrap CI excludes improvement), after the reviewer's leakage audit passes.

**Interpretation ladder (all informative):** (a) genuine incremental information;
(b) transcript captures almost everything available; (c) BOLD timing prevents useful
prospective decoding; (d) effect only within-subject; (e) apparent effect was leakage;
(f) only coarse dimensions are predictable.

**Experiments.** CM-5 comparison M_language vs M_fusion with a lag grid and holdout
discipline.

## H4 — Causal genealogy pruning (GATE: research finding)

**Statement.** The candidate dynamic SCM for thought dynamics contains testable
conditional independencies given the data; at least some edges are rejected, yielding a
pruned graph, and the set of unanswerable causal claims is explicitly documented.

**Falsification.** No conditional independence in the candidate graph is testable with
the available data (in which case the deliverable is the negative identification
result plus the future-experiment design).

**Experiments.** CM-8: conditional independence tests on lagged variables, with
permutation controls; documentation of unidentifiable claims.

## H5 — Prediction reveal changes trajectories (future; requires new data)

**Statement.** Under a randomized reveal condition, the post-reveal trajectory diverges
from the pre-reveal predicted trajectory by a measurable Branch Divergence Index, and
veto/redirect conditions produce measurable Agency Gain.

**Status.** DESIGN ONLY (CM-11, CM-12). No observational data can test H5; it requires
a randomized human experiment (ethics/IRB milestone).

## H6 — Recursive predictability (future; requires new data)

**Statement.** The probability of resisting/redirecting a revealed prediction is itself
predictable from pre-reveal state (Recursive Predictability Recovery > chance).

**Status.** DESIGN ONLY (CM-13).
