from pathlib import Path
ROOT = Path("/home/jovyan/work/causal-mind-v2")

# 1) current_state.md — project state
cs = ROOT / "docs" / "current_state.md"
t = cs.read_text()
old_state = (
    "`CM5_NULL_NO_INCREMENTAL_NEURAL_VALUE`\n"
    "(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`; CM-5 =\n"
    "`CM5_NULL`. OpenNeuro access RESTORED via authenticated selective acquisition.\n"
    "CM-5 decisive analysis complete: HRF-safe BOLD contains NO incremental\n"
    "prospective value for future thought beyond the frozen behavioral-history model\n"
    "+ motion/speech confounds, across h=1,3,5,10 and the N1-N3 capacity ladder.\n"
    "A clean, red-team-validated null.)"
)
new_state = (
    "`CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION`\n"
    "(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`; CM-5 = `CM5_NULL`;\n"
    "CM-6 = `CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION`. The project has moved from\n"
    "FORECAST to EXPLAIN/INTERVENE. CM-6A built an observational candidate SCM of\n"
    "thought dynamics: 0/84 candidate edges are causally identifiable (all blocked by\n"
    "unmeasured confounding incl. the per-subject GPT-rating baseline); the affect\n"
    "family's pooled skill is a between-subject GPT-baseline artifact (within-subject\n"
    "R^2 0.01-0.05). CM-6B audited public intervention datasets (best public test =\n"
    "ds005494; no public dataset tests voluntary redirection). CM-6D/E built the causal\n"
    "metrics + a counterfactual engine that refuses to label an unidentified\n"
    "counterfactual as causal. CM-6C/F/G/H/I designed the first own experiment\n"
    "(CM-6H pre-Oracle voluntary redirection) and gated THE ORACLE behind 6 unmet\n"
    "readiness criteria. Red-team: GO-WITH-CHANGES (all changes applied). No causal\n"
    "effect has been measured; no free-will claim.)"
)
assert old_state in t, "project-state block not found"
t = t.replace(old_state, new_state)
cs.write_text(t)
print("current_state.md: project state updated")

# 2) research_log.md — append CM-6 entry
log = ROOT / "docs" / "research_log.md"
entry = """
## 2026-09-16 — CM-6: Causal Genealogy (FORECAST -> EXPLAIN/INTERVENE)

- **Framing.** CM-5's frozen NULL (HRF-safe fMRI adds no incremental prospective value)
  motivates the transition from prediction `P(T_future | history)` to causation
  `P(T_future | do(X))`. Prediction != causation; CM-6 must not claim causal effects from
  observational association.
- **CM-6A (observational candidate SCM).** 118 subjects, 6436 thoughts; 14 GPT-rated
  dimensions + linguistic + temporal + semantic state. 7 analyses (lagged skill, CI
  structure, incremental value, transition asymmetries, cross-subject stability,
  mediator/moderator, identifiability audit). Result: **0/84 candidate edges causally
  identifiable** (unmeasured confounding). 39/272 CI edges survive BH-FDR; 0/126 mediator
  triples survive. **Red-team (CM-6J) found the "affect is strongest" headline is a
  between-subject GPT-rating-baseline artifact** (within-subject lag-1 R^2 0.01-0.05 vs
  pooled 0.05-0.20; GPT inflated vs human: joy +0.50, anxiety +0.27). Downgraded. The
  robust observational signal is the linguistic-load cluster (duration->gap r=0.828) and
  the semantic embedding.
- **CM-6B (public intervention dataset audit).** 16 candidates, 9 verified via S3/README.
  Best public `do(X)->future semantic state` = **ds005494** (E3 memory cue, N=20, iEEG,
  randomized open-loop stimulation). Closest affect handle = ds006583 (music->affect,
  N=43). **Gap: no public dataset tests voluntary redirection of a predicted thought (E8).**
- **CM-6D/E (causal machinery).** Metrics (CTE, BRP, persistence, divergence, decay) +
  SemanticBasin + matched-control sampler + a counterfactual engine that refuses to label
  an unidentified counterfactual as causal (enforced in code, 61/61 tests, ruff clean).
- **CM-6C/F/G/H/I (target ranking + experiment design + Oracle gate).** First public test
  = ds005494 (method validation). First own experiment = **CM-6H pre-Oracle** (voluntary
  redirection: CONTROL / SHAM / GENERAL REDIRECT / SPECIFIC CUE -> BRP), with CM-6J design
  fixes (sham-instruction demand control, cue-verbatim lexical-overlap rule, baseline-
  diversity floor, 4x4 Latin-square counterbalancing). THE ORACLE gated behind 6 unmet
  readiness criteria (CM-6I).
- **Red-team (CM-6J): GO-WITH-CHANGES.** No BLOCK-level leakage. All changes applied:
  affect downgrade, 3 factual doc errors fixed, BH-FDR added, CM-6H design fixes, CM-6
  claims registered (C-006..C-009).
- **Decision: CM6_OBSERVATIONAL_ONLY_NO_IDENTIFICATION** (CM-6A); the public test and the
  own experiment are designed, not executed (IRB required). Next: validate the method on
  ds005494, then seek IRB for CM-6H.
"""
log.write_text(log.read_text() + entry)
print("research_log.md: CM-6 entry appended")
