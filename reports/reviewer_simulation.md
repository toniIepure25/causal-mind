# External-Reviewer Simulation

Three simulated external reviewers, each with a different expertise and skepticism, review
the program (as it would be presented for a thesis / paper). For each concern, a prepared
response. Part of the `cm8-prehuman-v1.0` freeze. This is a *simulation* (self-red-team),
not a real peer review.

---

## Reviewer 1 — Cognitive scientist (skeptical of the prediction effect)

**Summary.** "An interesting attempt to forecast spontaneous thought. The effect is real
but small, and the test set is tiny. I'm not convinced this is more than a strong
persistence baseline."

**Concerns:**
1. The gain over the strongest baseline is only ~0.03 at h=1 and ~0.004 at h=10. Is this
   meaningful, or just a persistence artifact?
2. n=17 test subjects is too small to be confident.
3. You only report the semantic arm; the category arm is missing.

**Prepared responses:**
1. The gain is reported against the *strongest* horizon-specific baseline (not a weak one),
   with subject-level CIs that exclude 0 at every horizon, and it survives time-shuffled,
   transition-destroyed, and random-target nulls (p=0.0000). The *smooth monotonic decay* of
   the gain with horizon is the qualitative claim — it is the signature of a real,
   finite-horizon signal, not a persistence artifact (a pure persistence artifact would not
   decay smoothly to a lower bound). We are explicit that the effect is modest.
2. We report n=17 prominently as a limitation. The split is sealed and subject-disjoint
   (no leakage), and the inference is subject-level (no pseudo-replication). A larger-N
   replication is the natural next step; the power surface guides the required N.
3. The category arm is explicitly reported as **unvalidated** (a limitation, not a hidden
   omission). The semantic arm is the primary, pre-registered target.

**Likelihood of acceptance after response:** Moderate. The magnitude is the weak point; the
horizon + decay + null-robustness are the strong points.

---

## Reviewer 2 — Causal-inference statistician (skeptic of the causal method)

**Summary.** "The identification audit is a good idea, and validating the method on an
independent dataset before the real experiment is the right practice. But the BRP is an
unusual estimand, and I want to see the failure modes handled."

**Concerns:**
1. The BRP (probability the future leaves the predicted basin) is a strange primary
   estimand. Why not a standard ATE on a continuous outcome?
2. 7/9 adversarial cases give a misleading high BRP. That's a lot of failure modes.
3. The CM-7 validation is on a clinical iEEG dataset with no sham. What exactly does it
   validate?

**Prepared responses:**
1. The BRP is the pre-registered primary estimand because the intervention's *target* is
   the predicted trajectory: the scientifically meaningful question is whether the observed
   future leaves the *predicted* basin. A standard continuous ATE would not capture
   "did the intervention break the prediction." The BRP is calibrated (ghost pilot
   BRP_control ≈ 0.0785 ≈ 0.10 target) and is always reported with secondary diagnostics.
2. We disclose all 7 failure modes (magnitude-only change, lexical echo, tiny-basin
   miscalibration, volatility) and report the secondary diagnostics (cosine-direction,
   Mahalanobis, persistence, novelty) alongside the BRP in every case. The BRP stays PRIMARY
   (pre-registered); the diagnostics are the guardrails. This is a known, documented
   limitation, not a hidden one.
3. CM-7 validates the *method's structure* — randomized identification, the leakage audit,
   the destructive controls, and the subject-clustered inference — not the *thought*
   hypothesis. The specific effect is a null (we say so). The caveats (clinical population,
   no sham, retrieved not free state) are stated. What transfers to CM-8 is the method's
   *correctness under randomization*, which is exactly what CM-8 provides.

**Likelihood of acceptance after response:** Moderate-to-good. The method-validation framing
is strong; the BRP is the main point of contention (mitigated by calibration + diagnostics).

---

## Reviewer 3 — Methods / reproducibility reviewer

**Summary.** "The reproducibility story is unusually strong — frozen artifacts, a
clean-room bit-identical re-fit, sealed splits, an artifact hash manifest. I want to verify
the freeze is real and that nothing was tuned to the test split."

**Concerns:**
1. Is the forecaster truly frozen, or was it tuned on the test split?
2. Are the splits really subject-disjoint and sealed?
3. Can I reproduce the key numbers from the frozen artifacts?

**Prepared responses:**
1. The forecaster is a **frozen artifact** (`artifacts/cm8_forecaster/`, SHA-verified). A
   **clean-room re-fit** from source + data is **bit-identical** to the frozen artifact
   (`reports/cm8r_cleanroom/`). Hyperparameters (k, α) were selected on the VAL split only;
   the TEST split was never used for fitting or tuning.
2. The splits are **subject-disjoint** (no subject in more than one split) and **sealed**
   (seal `67505261…`, in `data/manifests/cm2_split_seal.json`, SHA-verified). There are no
   random row splits on temporal data.
3. Yes. Every key number maps to a committed script + frozen artifact (see the
   reproducibility traceability table). The commands are in
   `docs/releases/cm8_prehuman_v1.md`. The full test suite + `ruff` pass. No network access
   is required at inference.

**Likelihood of acceptance after response:** Good. The reproducibility story is the program's
strongest asset; a methods reviewer should be satisfied.

---

## Overall

- **Strongest asset:** reproducibility (frozen artifacts, clean-room bit-identical, sealed
  splits, hash manifest).
- **Weakest point:** the modest prediction effect + small test set (Reviewer 1).
- **Main contention:** the BRP estimand (Reviewer 2), mitigated by calibration + diagnostics.
- **No reviewer** challenges the honesty of the negative results or the absence of a
  free-will claim — the claim ceiling is respected.

See `docs/reviewer_response_preparation.md` for the consolidated response bank.
