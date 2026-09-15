#!/usr/bin/env python3
"""Update project docs with the CM-5 decisive NULL result."""
from pathlib import Path

ROOT = Path("/home/jovyan/work/causal-mind-v2")

# 1) Claims registry: insert C-005 after C-004
claims = ROOT / "docs" / "claims_registry.md"
c = claims.read_text()
c005 = (
    "| C-005 | In the ds006067 think-aloud fMRI cohort (106 subjects, 73/17/16 "
    "subject-disjoint after pre-registered F2 tSNR + alignment gates), BOLD in "
    "the HRF-safe window [onset-21s, onset-6s] contains NO incremental "
    "predictive value for target-thought content beyond the frozen CM-3 "
    "behavioral-history model (k=3 MiniLM, alpha=100) plus 40 motion/speech "
    "nuisance regressors: IncrementalNeuralGain (M4-M2) is negative at every "
    "horizon h=1,3,5,10 (primary N2/Schaefer-400: -0.088/-0.085/-0.085/-0.090, "
    "95% CIs excluding 0, 0/16 test subjects positive) and non-positive across "
    "the capacity ladder (N1 7-net ~-0.001, N3 PCA-50 ~-0.016, N2 400-parcel "
    "~-0.085); NC4 (nuisance-only) -> 0; destructive controls NC1/2/3/5/6 "
    "confirm no hidden shortcut; robust to motion-screen sensitivity. Detection "
    "threshold ~0.005 (N1) / ~0.02 (N3) / ~0.11 (N2) cosine. A clean null: "
    "HRF-safe brain activity does NOT extend the behavioral predictive horizon "
    "for thought content in this task. NO causal/free-will claim; null is "
    "conditional on the frozen baseline, window, horizons, and dataset. | L5 | "
    "CM-5 decisive report + red-team GO (2026-09-14) | validated (negative "
    "result) |\n"
)
anchor = "| C-004 |"
idx = c.find(anchor)
assert idx >= 0, "C-004 not found"
eol = c.find("\n", idx)
c = c[:eol + 1] + c005 + c[eol + 1:]
claims.write_text(c)
print("claims_registry.md: C-005 inserted")

# 2) Research log: append CM-5 section
log = ROOT / "docs" / "research_log.md"
entry = """
## 2026-09-14 — CM-5 decisive analysis: clean NULL (no incremental neural value)

- **MRI-eligible cohort (outcome-independent).** Metadata-first audit of all
  118 subjects (availability + confounds QC + HRF-safe target counts). Frozen
  eligibility criteria (CM5-ELIG-1, hash-sealed): data availability (URL-path
  identity guard), file validity, >=20 steady-state HRF-safe targets (AM-1:
  onset>=36s), severe-motion screen (mean FD>1.0mm), behavioral compatibility.
  Excluded: sub-002 (OpenNeuro pointer-object anomaly, guard-fire), sub-067/
  087/110 (<20 targets), sub-089 (mean FD 1.207mm). Cohort 113 (79/18/16),
  sealed (reports/cm5_cohort_seal.json).
- **BOLD acquisition.** All 113 subjects' preproc BOLD + masks downloaded via
  the guarded, hash-verified, resumable fetcher (226 files, 0 mismatches, 0
  hash failures, 87.5 GB). Storage verified (87.5 GB vs ~102 TB free).
- **Post-acquisition gates (pre-registered, outcome-independent).** F2 tSNR
  gate excluded 6 (tSNR < 5th percentile; CM5-F2-TSNR-1). Cohort-level
  N-GATE-1 alignment audit found sub-036 with 2 OSF thoughts lacking a raw MRI
  event (CM5-ALIGN-1, excluded). Final cohort 106 (73/17/16).
- **Decisive result (CM5_NULL).** IncrementalNeuralGain (M4-M2) is NEGATIVE at
  every horizon h=1,3,5,10 for the primary N2 (Schaefer-400): -0.088/-0.085/
  -0.085/-0.090 (95% CIs exclude 0; 0/16 test subjects positive). Capacity
  ladder: N1 (7 nets) ~-0.001, N3 (PCA-50) ~-0.016, N2 (400) ~-0.085 — the
  degradation scales with dimensionality (noise signature, not a real signal).
  NC4 (nuisance-only) -> 0; NC1/2/3/5/6 preserve the negative gain (no
  correspondence to destroy). M0=0.32 (behavior), M2=0.32, M4=0.23.
- **Red-team: GO (conditional).** Fixed a CI-reporting bug (bootstrap_ci
  returns mean,lo,hi) and removed a post-cutoff speech feature (lag-to-next-
  onset). Confirmed no leakage (HRF-safe window, causal z-score, N3 fit on
  train only), the negative gain is expected Ridge noise (linear per-dim cost),
  and the null is strongest where power exists (N1/N3). Licensed claim is a
  scoped negative L5 result; NOT licensed: "brain has no prospective info"
  (underpowered for small high-dim effects), any causal/free-will claim.
- **Reproducibility.** 112/112 tests pass; synthetic end-to-end (injected
  neural signal) gives positive gain that collapses under all controls — the
  pipeline can detect a real signal.
- **Next.** Commit + push the CM-5 null. The neural incremental-value question
  is answered (null) for this task/window/horizons/baseline.
"""
log.write_text(log.read_text() + entry)
print("research_log.md: CM-5 section appended")

# 3) Current state: update project state + stage
cs = ROOT / "docs" / "current_state.md"
t = cs.read_text()
t = t.replace(
    "`CM5A_REAL_DATA_SMOKE_PASS`\n(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`. OpenNeuro access is\nRESTORED via authenticated selective acquisition; CM-5 proceeds to the\nMRI-eligible cohort definition, metadata-first and outcome-independent.)",
    "`CM5_NULL_NO_INCREMENTAL_NEURAL_VALUE`\n(CM-1 = `CM1_PASS`; CM-2 = `CM2_PASS`; CM-3 = `CM3_PASS`; CM-5 =\n`CM5_NULL`. OpenNeuro access RESTORED via authenticated selective acquisition.\nCM-5 decisive analysis complete: HRF-safe BOLD contains NO incremental\nprospective value for future thought beyond the frozen behavioral-history model\n+ motion/speech confounds, across h=1,3,5,10 and the N1-N3 capacity ladder.\nA clean, red-team-validated null.)",
)
cs.write_text(t)
print("current_state.md: project state updated")
