# CAUSAL MIND — One-Page Brief for the Supervisor

**For:** University of Vienna Master's thesis supervision
**Date:** 2026-09-20 · **State:** `CM8R_PREHUMAN_HARDENED` (pre-human freeze `cm8-prehuman-v1.0`)
**Bottom line:** A complete, reproducible, pre-human research program on predicting and
causally redirecting the human thought stream. **No human data has been collected.** The
only things left to do before any human experiment are three external approvals: your
sign-off, ethics approval, and the pilot.

## The question

Can we **predict** the future of a person's thought stream from its recent past, and can
a **prediction-conditioned intervention** causally change it?

## What has been done (all public data + synthetic; nothing on humans)

- **Prediction works (modestly).** A simple linear model over a short (k≈3) window of
  frozen MiniLM thought embeddings predicts the **next** thought's semantics
  (held-out cosine **0.362 [0.352, 0.372]**, above all 8 baselines) and predicts
  **future** thoughts at every horizon h=1..10, with a smooth decay of the gain
  (+0.035 at h=1 → +0.004 at h=10). Subject-disjoint, sealed, reproduced exactly.
- **The neural signal adds nothing (a clean null).** HRF-safe fMRI BOLD provides **no**
  incremental value for thought content beyond the behavioral model (gain −0.088, all
  subjects negative, p=1.0). Reported as a null, not reopened.
- **Observational thought dynamics are not causally identifiable.** 0 of 84 candidate
  edges are identifiable (unmeasured confounding). This is why the confirmatory step is
  a *randomized* experiment, not an observational one.
- **The causal-inference method is validated.** On an independent public dataset
  (ds005494, N=20), the framework correctly identifies and estimates a
  randomized causal effect (ATE −0.039, p=0.073 — a valid null; the *method* is the
  result). Leakage audit passed.
- **The confirmatory experiment is frozen and pre-human hardened (10/10 gates).**
  The participant-facing forecaster is frozen and reproducible (clean-room bit-identical);
  the offline realtime engine runs the full trial lifecycle (p95 ≈ 478 ms); the
  randomization is audited; privacy is hardened (no raw text leaves the machine, no
  remote LLM); all 10 pre-human gates pass.

## What the confirmatory experiment (CM-8) tests

A **within-subject, randomized, 4-condition** test: CONTROL / SHAM / GENERAL-REDIRECT /
SPECIFIC-CUE. Primary outcome: **BRP** — the probability the observed future leaves the
frozen predictor's predicted-future basin. N=20, 24 trials, α=0.05 two-sided,
B=10,000 permutations. This is the first experiment that tests **voluntary redirection of
a predicted thought** — a gap no public dataset fills.

## What I need from you

1. **Sign-off** on the frozen protocol and the pre-human freeze.
2. **Ethics submission** (University of Vienna Ethics Committee). The package is ready in
   `docs/ethics/`. **Submission deadline 5 Oct 2026** for the **5 Nov 2026** meeting.
   For a Master's thesis the supervisor / responsible study-law body submits; I prepare.
3. **Pilot authorization** (a small, gated pilot before the confirmatory run).

## Where to look

- Start here: `docs/supervisor/START_HERE.md`
- Freeze + hashes: `docs/releases/cm8_prehuman_v1.md`
- Master summary: `docs/CAUSAL_MIND_master_summary.md`
- Claim-level evidence: `docs/claims/evidence_matrix.md`
- Ethics package: `docs/ethics/`
- Questions for you: `docs/supervisor/questions_for_supervisor.md`

## What I am NOT claiming

- No free-will claim (proven or disproven).
- No claim that the (null) public-intervention effect is real.
- No causal claim from the observational data (0/84 identifiable).
- The prediction effects are modest; the test set is small (n=17).

*This is a freeze document. It does not modify any frozen phase.*
