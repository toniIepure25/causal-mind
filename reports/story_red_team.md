# Scientific Story Red Team

A red-team of the program's scientific story: the strongest skeptical readings, the
weaknesses, and the honest defenses. Part of the `cm8-prehuman-v1.0` freeze. The goal is to
surface the weak points **before** a reviewer does.

## The story (as told)

"Spontaneous thought is partly forecastable (a real, finite semantic signal with a
measurable horizon). The observational thought stream is not causally identifiable, so we
validated a causal-inference method on an independent public dataset and froze a
pre-human-hardened randomized confirmatory experiment to test whether a predicted thought
can be voluntarily redirected."

## Attack 1 — "The prediction effect is too small to matter."

- **Skeptic:** 0.36 cosine and a +0.03 gain at h=1 is modest; a marginal baseline is already
  0.31. Why should anyone care?
- **Honest defense:** We do **not** claim the effect is large. The contribution is the
  *establishment* of a real, finite, forecastable signal and its *horizon* (TPH ≥ ~10
  thoughts), not its magnitude. The smooth decay of the gain with horizon is the qualitative
  result — it is the pattern a real signal produces. The horizon is what makes the
  intervention question meaningful.
- **Residual risk:** a reviewer may still dismiss the magnitude. Mitigation: lead with the
  horizon and the decay, report the exact CIs, and be explicit that the effect is modest.

## Attack 2 — "The test set is tiny (n=17)."

- **Skeptic:** 17 test subjects is small; the CIs are tight but the evidence base is thin.
- **Honest defense:** The split is sealed and subject-disjoint (no leakage); the CIs are
  subject-level (no pseudo-replication); the result survives three nulls (p=0.0000). We
  report n=17 prominently as a limitation. The effect's *reliability* (consistent across
  subjects, above baselines, null-robust) is the claim, not its precision.
- **Residual risk:** a reviewer may want a larger test set. Mitigation: state that a
  larger-N replication is the natural next step (and the power surface guides it).

## Attack 3 — "You can't claim causation from this."

- **Skeptic:** The observational data is confounded; where is the causal evidence?
- **Honest defense:** We make **no** causal claim from the observational data (0/84 edges
  identifiable — we say so). The causal evidence is (a) the *method* validated on a
  randomized public dataset (CM-7), and (b) the *frozen randomized* confirmatory design
  (CM-8), which is not yet run. We are explicit that the human causal result does not exist
  yet.
- **Residual risk:** a reviewer may conflate the method validation with a human causal
  result. Mitigation: Paper 2 is titled and framed as "method validation + frozen design,"
  not "a causal result."

## Attack 4 — "The BRP is a strange estimand with known failure modes."

- **Skeptic:** 7/9 adversarial cases give a misleading high BRP; why trust it?
- **Honest defense:** We disclose the failure modes and report the secondary diagnostics
  (cosine-direction, Mahalanobis, persistence, novelty) alongside the BRP in every case.
  The BRP stays PRIMARY because it is the pre-registered estimand; the diagnostics are the
  guardrails. The ghost pilot (BRP_control ≈ 0.0785 ≈ 0.10 target) shows it is calibrated.
- **Residual risk:** a reviewer may prefer a different primary estimand. Mitigation: the
  diagnostics are pre-registered secondary outcomes; the BRP's calibration is evidenced.

## Attack 5 — "The CM-7 'validation' is on a weird clinical dataset."

- **Skeptic:** ds005494 is a clinical iEEG stimulation study, not thought redirection; what
  does it validate?
- **Honest defense:** It validates the *method* (identification + estimation of a
  randomized causal effect with the right controls and leakage audit), not the *thought*
  hypothesis. The specific effect is a null (we say so). The method is what transfers to
  CM-8.
- **Residual risk:** a reviewer may question the transfer. Mitigation: state the caveats
  (clinical population, no sham, retrieved not free state) and that the method's
  *structure* (randomized identification + leakage audit + destructive controls) is what is
  validated.

## Attack 6 — "This is a free-will project in disguise."

- **Skeptic:** The whole framing (predicting and redirecting thought) smells like a free-will
  claim.
- **Honest defense:** We make **no** free-will claim, and we say so in every document. The
  claim ceiling is L0–L6 (prediction + validated method + frozen design). Free will is out
  of scope. The claim-language linter enforces this (0 BLOCK-level free-will overclaims).
- **Residual risk:** a reviewer may read between the lines. Mitigation: the known/unknown
  document explicitly lists "any statement about free will" as UNKNOWN/out-of-scope.

## Attack 7 — "The synthetic Oracle lab is not science about humans."

- **Skeptic:** CM-9A is a toy synthetic world; what is it for?
- **Honest defense:** It is a *separate* research direction (a theory of prediction vs.
  intervention), explicitly synthetic (no real-human claim). It is useful for (a) choosing
  detectable interventions and (b) interpreting the BRP. We do not claim it models human
  thought.
- **Residual risk:** a reviewer may see it as scope creep. Mitigation: it is clearly
  separated from the CM-8 confirmatory experiment and labeled synthetic.

## Net assessment

The story is **defensible** if (and only if) we keep the claim ceiling honest: modest
prediction, no observational causation, a validated method, a frozen (not-yet-run)
confirmatory design, and no free-will claim. The weak points (small effect, small test set,
strange estimand, clinical validation dataset) are all **disclosed** with honest defenses.
The single biggest risk is a reviewer conflating the method validation with a human causal
result — Paper 2's framing must prevent that.
