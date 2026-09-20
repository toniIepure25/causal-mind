# Repository Hygiene Audit

A hygiene audit of the repository at the `cm8-prehuman-v1.0` freeze. Part of CM-PUB.

## Audit results

| check | status | notes |
| --- | --- | --- |
| No credentials in tracked files | PASS | scan: 9 hits, all false positives (descriptions, `get-token` commands, test fixtures for the credential scanner); no real secrets |
| No participant data (new) | PASS | no human data collected; the only tracked thought data is the PUBLIC OSF `a56rm` transcripts (119 files / 3.2 MB, required for reproducibility) |
| No large raw datasets tracked | PASS | no tracked file > 500 KB; the 28 MB forecaster weights are gitignored (SHA-verified) |
| `.gitignore` covers scratch + large artifacts | PASS | `*_msg.txt`, `ci_msg.txt`, `data/neural/`, `artifacts/cm8_forecaster/ridge_weights.npz`, caches |
| Committed reports match the freeze | PASS | all CM-8R + CM-9A reports committed; SHA-verified |
| Test suite passes | PASS | full `pytest` green (requires `HF_HOME=/home/jovyan/work/.hf-home`) |
| `ruff` clean | PASS | `ruff check src tests scripts` clean |
| No dead top-level files | PASS | scratch commit-message files gitignored |
| Consistent directory layout | PASS | `src/causal_mind/`, `data/scripts/`, `data/manifests/`, `artifacts/`, `reports/`, `docs/`, `papers/`, `tests/` |
| Every claim has a registry entry | PASS | C-001..C-012 in `docs/claims_registry.md` |
| Every result has a report + reproduction command | PASS | `docs/claims/evidence_matrix.md` + reproducibility traceability table |

## Actions taken in CM-PUB

- Added `docs/releases/cm8_prehuman_v1.md` (the freeze).
- Added `docs/CAUSAL_MIND_master_summary.md` and `docs/claims/evidence_matrix.md`.
- Added the supervisor package (`docs/supervisor/`).
- Added the paper drafts (`papers/`).
- Added the science docs (`docs/science/`), the audits (`reports/`), the claim-language
  linter (`data/scripts/cm_pub_claim_linter.py`), `CITATION.cff`, and the license/data-use
  audit.
- Gitignored the scratch commit-message files (`*_msg.txt`, `ci_msg.txt`).

## Remaining hygiene items (non-blocking)

- **CITATION.cff** added (see `CITATION.cff`).
- **License** clarified in `docs/science/license_data_use_audit.md`.
- The 119 public thought transcripts are tracked (3.2 MB) for reproducibility; if a future
  reviewer objects, they can be moved to a gitignored cache with a manifest (the SHA
  manifest already exists).

## Result

**HYGIENE PASS.** No secrets, no new participant data, no large raw datasets, clean tests +
lint, consistent layout, full claim/report/reproduction traceability.
