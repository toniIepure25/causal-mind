# CM-8R Operational Design — Manipulation Check, Report-Reactivity, Pilot Rules, Blinding

Pre-human (no human data). Workstream B per `docs/cm8r_confirmatory_boundary.md`. These
are OPERATIONAL / DESIGN items for the pilot and the confirmatory run; they do NOT change
the frozen CM-8 confirmatory protocol (Workstream A).

## S19 — Manipulation check design

Purpose: verify that participants EXPERIENCED the intended intervention (not just that the
code ran). A manipulation check is a SECONDARY, pre-declared measure; it is NOT the
primary endpoint and is NOT used to select which trials count.

Design (administered at the END of the session, after all 24 trials):
- Perceived intervention (1-7): "How much did the on-screen prompt change the direction
  of your thinking?" (anchored: 1 = not at all, 7 = completely).
- Condition recognition (forced choice): "Which of the following best describes the
  prompt you saw?" (4 options matching the 4 conditions, plus "I don't know").
- Believability (1-7): "How believable was the prompt as a real thinking task?"

Interpretation:
- A HIGH perceived-intervention score in GENERAL/CUE vs CONTROL/SHAM supports the
  manipulation (the intervention was experienced).
- A LOW condition-recognition accuracy in SHAM vs GENERAL/CUE supports BLINDING (the
  sham is believable).
- The manipulation check is reported as a SECONDARY analysis; it does NOT gate the
  primary ATE. If the manipulation fails (participants did not experience the
  intervention), the primary result is interpreted with that caveat (a null may reflect
  a failed manipulation, not a true null).

## S20 — Report-reactivity analysis

Purpose: the act of REPORTING thoughts (typing them into the app) may CHANGE the thoughts
(report reactivity / the observer effect). This is a known confound in thought-capture
studies.

Mitigations (pre-declared):
- The thought-capture is a SINGLE, brief typing task (one sentence), not an open-ended
  essay. This minimizes the time spent "thinking about thinking."
- The CONTROL and SHAM conditions ALSO require thought capture, so report-reactivity is
  a common-mode confound (it affects all conditions equally). The PRIMARY estimand is
  the ATE (intervention vs control), which differences out the common-mode reactivity.
- The BRP is computed on the CAPTURED thoughts (post-capture), so the reactivity is part
  of the measured process (we measure the effect on the reported thought stream, which is
  the actual intervention target).

Secondary analysis (exploratory):
- Compare the BRP on the FIRST post-capture thought (most reactivity) vs the LATER
  post-capture thoughts (less reactivity). If the effect is concentrated in the first
  thought, report-reactivity may be inflating it.
- Compare the typing SPEED (characters/second) across conditions. A change in typing
  speed across conditions would suggest the intervention changed the cognitive process
  (not just the content).

## S22 — Pilot GO / ITERATE / STOP rules

The pilot is OPERATIONAL (not a treatment-effect test). The GO/ITERATE/STOP decision is
based on OPERATIONAL metrics, NOT on the primary ATE (the pilot is under-powered for the
ATE; using the ATE to decide would be a statistical error).

GO (proceed to the confirmatory run) if ALL of:
- 100% of trials are analysis-valid (no technical failures).
- The forecaster runs offline (no Qwen / no internet) on the pilot hardware.
- The session completes within the burden budget (~30-45 min).
- The manipulation check shows the intervention was experienced (perceived-intervention
  > 4/7 in GENERAL/CUE).
- The BRP_control is within the calibrated range (0.05-0.20, consistent with the
  held-out calibration ~0.08).
- No privacy incidents (no PII leaks, no remote transmission).

ITERATE (fix and re-pilot) if ANY of:
- A technical failure rate > 5% (the engine should fail loudly, but a high rate is a
  signal to fix).
- The forecaster latency p95 > 2s on the pilot hardware (the participant experience
  would be too slow).
- The manipulation check shows the intervention was NOT experienced (perceived-
  intervention < 3/7 in GENERAL/CUE).
- A privacy incident occurred.

STOP (do not proceed to human data) if ANY of:
- A privacy breach (PII leaked, remote transmission, identity recoverable).
- A safety concern (a participant was distressed by the intervention).
- The forecaster cannot run offline (a hard requirement).

## S28 — Analysis blinding

Purpose: the ANALYSIS is blinded to the condition assignment, so the analyst cannot
subconsciously steer the analysis toward a desired result.

Design:
- The analysis pipeline (the ATE + permutation test) takes the trial data + the condition
  labels as INPUT, but the ANALYST does not see the condition labels during the analysis.
  The condition labels are stored in a SEPARATE, access-controlled file that is only
  unblinded AFTER the primary analysis is locked.
- The primary analysis (ATE_GENERAL, ATE_CUE vs pooled CONTROL/SHAM) is computed by a
  SCRIPT (not by hand), so the analyst cannot steer it. The script is versioned and the
  analysis is reproducible (clean-room, per CM8R_REPRODUCIBILITY_PASS).
- The unblinding procedure: (1) the primary analysis is run and locked (the ATE + p-value
  are recorded); (2) the condition labels are unblinded; (3) the secondary analyses are
  run. The primary result is NOT changed after unblinding.

## S29 — Experimenter blinding

Purpose: the EXPERIMENTER (the person running the session) is blinded to the condition
assignment, so they cannot (even subconsciously) influence the participant or the data.

Design:
- The randomization manifest is FROZEN and the experimenter does NOT see which condition
  each trial will be. The engine (not the experimenter) renders the intervention.
- The experimenter's role is limited to: setting up the session, monitoring for technical
  issues, and administering the manipulation check at the end. They do NOT see the
  on-screen prompts (the participant sees them directly).
- The intervention is rendered by the ENGINE (the frozen randomizer + intervention
  renderer), not by the experimenter. This ensures the experimenter cannot know (or
  influence) the condition.
- The manipulation check is administered by the engine (self-report), not by the
  experimenter (to avoid the experimenter's influence).

## Summary

These operational items (manipulation check, report-reactivity, pilot rules, analysis
blinding, experimenter blinding) are the GUARDRAILS for the pilot and the confirmatory
run. They are pre-declared, do NOT change the frozen confirmatory protocol, and are
designed to protect the integrity of the primary result (the ATE).
