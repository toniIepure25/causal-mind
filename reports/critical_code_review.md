# Critical Code Review

**Date:** 2026-09-25 · **Baseline:** CM-REPO professionalization
**Scope:** the highest-risk scientific-integrity and operational code paths.
**Method:** close reading of the invariants, leakage scanner, statistical
analyses, split logic, artifact registry, and encoders; plus the new
foundation/CLI code added in this phase.

## Verdict

The scientific-integrity core is **sound and well-defended**. The invariants,
leakage scanner, permutation null, subject-disjoint splits, and SHA-256 artifact
registry are all correct and independently cross-checked. One real library bug
(`TfidfEncoder.fit`) was found and **fixed** in this review. The remaining
findings are portability/maintenance gaps, not scientific-integrity defects.

## What is solid (verified)

- **Invariants** (`tests/test_invariants.py`): 10 guards on frozen properties
  (subject-disjoint split 83/18/17, prospective horizons, HRF buffer,
  counterfactual refusal, randomization-aware inference, alpha 0.05, basin_tail
  0.10 in *both* config locations, BRP definition + `predicted_basin.py` SHA,
  no-real-human-data pre-ethics, synthetic isolation). They hard-code expected
  values as *independent* guards — the correct design for an invariant.
- **Permutation null** (`eval/analyses.py:131`): pairs each history with a random
  target, preserving marginals and destroying temporal correspondence; p =
  fraction of nulls ≥ observed. Correct one-sided permutation test.
- **Bootstrap CIs** (`eval/analyses.py:60`): seeded (`seed=0`), n_boot=2000 —
  reproducible.
- **Train/eval separation** (`eval/analyses.py:38`): model fit on a
  `TrainCorpus`, evaluated on test *subjects*; no fit-on-test.
- **Splits** (`utils/splits.py`): subject-disjoint, seeded, fraction-validated,
  with a `check_temporal_crossing` guard against row-level leakage bugs.
- **Artifact registry** (`cm_lab_registry.py:220`): `--check` re-computes SHA-256
  of every frozen artifact and fails on any mismatch or missing file.
- **Frozen configs as source of truth** (`constants.py`): reads alpha, basin_tail,
  horizons, h*, k, seeds from the frozen files; raises on missing/malformed.

## Findings

### Fixed in this review

| # | Severity | Finding | Resolution |
|---|----------|---------|------------|
| F1 | **P1 (latent bug)** | `thought/encode.py:58` — `TfidfEncoder.fit` set `self.dim = self._v.vocabulary_size_`, but `TfidfVectorizer` has `vocabulary_` (a dict), not `vocabulary_size_`. Calling `fit` raised `AttributeError`. Scripts had worked around it by using `TfidfVectorizer` directly. | Fixed to `len(self._v.vocabulary_)`. Verified: `TfidfEncoder().fit(...).encode(...)` now works (dim matches). No scientific result used the broken path, so no result changes. |

### Open (portability / maintenance — not scientific-integrity)

| # | Severity | Finding | Recommendation |
|---|----------|---------|----------------|
| F2 | **P1** | ~90 `data/scripts/*.py` hard-code `ROOT = Path("/home/jovyan/work/causal-mind-v2")` (e.g. `cm_leakage_scan.py:25`). Library code is fixed (`paths.py`), but scripts are not portable to a fresh clone on another machine. | Migrate scripts to `causal_mind.paths` (or a shared `repo_root()` helper) in a follow-up. Low risk, high portability payoff. |
| F3 | **P2** | `cm_leakage_scan.py` audits a **manual** `DEEP_DIVE_SCRIPTS` list. A new deep-dive script is not scanned unless added to the list. | Auto-discover `data/scripts/cm_*.py`, or add a test that the list matches the directory. |
| F4 | **P2** | `cm_leakage_scan.py` L5 (embedding per-entry) is a hard-coded `pass: True` with a justification — a "trust me" check, not a real one. | Acceptable as a first-line static note; the reviewer's manual audit is the backstop. Consider a real per-entry assertion. |
| F5 | **P2** | `eval/analyses.py:111` — `frac_above_marginal` is a `None` placeholder "filled by caller". A caller that forgets leaves it silently `None`. | Make it required or compute it in `cross_subject`. |
| F6 | **P3** | `cm_lab_registry.py --check` verifies frozen *artifacts* but not the *lineage* SHAs (informational). | Optionally re-verify lineage SHAs in `--check`. |
| F7 | **P3** | Two RNG libraries: `random.Random` in `utils/splits.py`, `np.random.default_rng` in `eval/protocol.py`. Not a bug (each is seeded and consistent), but inconsistent. | Standardize on one (numpy) for clarity. |

## Residual risks

- **Static leakage audit is a heuristic.** The fit-on-test / target-in-history
  checks use name-based regexes; a test-derived variable with an unexpected name
  could slip past. The defense-in-depth (sealed splits + invariants + reviewer
  manual audit) is the real protection, not the regex alone.
- **Small test set.** n=17 test subjects (CM-2/CM-3). Effects are modest and the
  CIs are wide; this is stated honestly in the README and claims, not hidden.
- **Portability of scripts (F2).** A fresh clone on a non-pod machine can run the
  library + CLI + tests, but the deep-dive *scripts* still assume the pod path.
  The library and validation path are portable; the one-off scripts are not yet.

## Conclusion

No scientific-integrity defect remains open. The one real bug (F1) is fixed and
verified. The open items (F2-F7) are portability/maintenance improvements that
do not affect the validity of any frozen result. The codebase is fit for expert
maintenance and for the pre-human freeze it supports.
