# Vision

Causal Mind is a research program to build a **causal world model of human thought**:
a model of the latent cognitive state `Z` that (a) reconstructs how a thought came to be,
(b) forecasts where it is going, and (c) identifies which interventions — internal
(volition, attention, goals) or external (cues, feedback, prediction reveal) — can
**causally redirect** the trajectory.

The program is staged so that each stage produces falsifiable evidence before the next
begins:

| Stage | Phase | Question |
| --- | --- | --- |
| OBSERVE | CM-1, CM-2 | Can we capture thought events and their neural correlates reproducibly? |
| REPRESENT | CM-2, CM-6 | Can we build a stable, validated Thought State representation? |
| FORECAST | CM-3, CM-4 | Is the next thought (and multi-step futures) predictable above strong baselines? |
| EXPLAIN | CM-5, CM-7, CM-8 | Does brain state carry prospective information beyond thought history? What is the candidate causal structure? |
| INTERVENE | CM-9, CM-11 | Can we simulate `P(future | do(X))` under identified assumptions? |
| REDIRECT | CM-11, CM-12 | Can a randomized intervention change the predicted trajectory? |
| PREDICT THE ESCAPE | CM-13 | Can resistance to a revealed prediction itself be predicted? |

Primary public data: OpenNeuro **ds006067** (think-aloud spontaneous thought + fMRI).
Extension: public EEG datasets of spontaneous thought / mind wandering (CM-10).

## What this is NOT

- Not a claim about free will. The claims ladder (Level 0-8) in
  `docs/claims_registry.md` forbids wording a predictive result as a causal one, and
  forbids any "free will proven/disproven" claim.
- Not a brain-decoding showcase. The central scientific comparison is
  **incremental prospective information** (brain + language vs language alone), not raw
  decoding accuracy.
- Not a large-model project. Compute is one A100-40GB; models are sized to the data.

## North Star

The single most important early experiment:

> On subject-disjoint splits, does the joint model of thought history + neural state
> predict future thought dimensions better than the best language-only model — and if
> not, what does that tell us about where prospective information lives?

A clean negative answer is a publishable, program-advancing result.
