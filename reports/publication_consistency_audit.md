# Publication Consistency Audit

Cross-document consistency check for the `cm8-prehuman-v1.0` freeze. Verifies that all
public-facing documents agree on the key values, states, and claims. Part of CM-PUB.

## Method

Each key fact is checked across the documents that state it. A fact is **CONSISTENT** if all
documents agree; **INCONSISTENT** if any disagree (action required).

## Key facts and their sources of truth

| fact | source of truth | value |
| --- | --- | --- |
| project state | `docs/current_state.md` | `CM8R_PREHUMAN_HARDENED` |
| freeze SHA | `docs/releases/cm8_prehuman_v1.md` | `8a9d5dd` (tag `cm8-prehuman-v1.0`) |
| CM-2 held-out semantic cosine | `reports/cm2_results.json` | 0.3623 [0.3523, 0.3720] |
| CM-2 strongest baseline (B0) | `reports/cm2_results.json` | 0.3167 [0.3078, 0.3250] |
| CM-3 h=1 gain | `reports/cm3_results.json` | +0.0349 [0.0253, 0.0445] |
| CM-3 h=10 gain | `reports/cm3_results.json` | +0.0044 (CI excl. 0) |
| CM-5 N2 gain (h=1) | `reports/cm5_decisive_results.json` | −0.088 (0/16 positive, p=1.0) |
| CM-6 identifiable edges | `reports/cm6_observational_results.json` | 0/84 (analysis_7) |
| CM-7 ATE | `reports/cm7_results.json` | −0.0386, p=0.0733, CI [−0.079, 0.002] |
| CM-8 BRP_control (ghost) | `reports/cm8r_ghost_pilot/` | 0.0785 (target 0.10) |
| CM-8R gates | `reports/cm8r_readiness/` | 10/10 |
| engine total p95 | `reports/cm8r_latency/` | 478.0 ms (cold 876.5 ms) |
| forecaster config SHA | `artifacts/cm8_forecasting_freeze_manifest.json` | `dbcbe443…` |
| forecaster weights SHA | `artifacts/cm8_forecasting_freeze_manifest.json` | `7b13d52c…` |

## Cross-document checks

| fact | master_summary | evidence_matrix | one_page | tech_brief | paper1 | paper2 | paper3 | release | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| project state = CM8R_PREHUMAN_HARDENED | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | CONSISTENT |
| freeze SHA 8a9d5dd / tag | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | CONSISTENT |
| CM-2 0.3623 [0.3523, 0.3720] | ✓ | ✓ | ✓ (0.362) | ✓ | ✓ | — | — | ✓ | CONSISTENT |
| CM-2 B0 0.3167 [0.3078, 0.3250] | ✓ | ✓ | — | ✓ | ✓ | — | — | — | CONSISTENT |
| CM-3 h=1 gain +0.0349 | ✓ | ✓ | ✓ (+0.035) | ✓ | ✓ | — | — | — | CONSISTENT |
| CM-5 −0.088, 0/16, p=1.0 | ✓ | ✓ | ✓ | ✓ | — | — | — | — | CONSISTENT |
| CM-6 0/84 identifiable | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | CONSISTENT |
| CM-7 ATE −0.0386, p=0.0733 | ✓ | ✓ | ✓ | ✓ | — | ✓ | — | — | CONSISTENT |
| BRP_control 0.0785 | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | CONSISTENT |
| 10/10 gates | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | CONSISTENT |
| engine p95 478 ms | ✓ | ✓ | — | ✓ | — | ✓ | ✓ | ✓ | CONSISTENT |
| forecaster SHAs | — | ✓ | — | — | — | — | — | ✓ | CONSISTENT |

## Claim-level consistency

| check | status |
| --- | --- |
| No claim worded above its level (L0–L8) | CONSISTENT (evidence matrix enforces) |
| No free-will claim in any document | CONSISTENT (linter: 0 BLOCK) |
| No causal claim from observational data | CONSISTENT (0/84 stated everywhere) |
| CM-7 effect stated as a null (not a positive) | CONSISTENT |
| CM-5 stated as a clean null (not reopened) | CONSISTENT |
| CM-8 stated as "not yet run" (ethics-gated) | CONSISTENT |

## Rounding note

The one-pager and pitch use rounded values (0.362, +0.035, −0.088, 0.0785) for readability;
the master summary, evidence matrix, and papers use the full-precision values. This is
intentional (rounded for a busy reader, exact for the record) and is **not** an
inconsistency. The exact values always appear in the evidence matrix and the reports.

## Result

**ALL CONSISTENT.** No document contradicts the source-of-truth reports or another
document. The claim-language linter reports 0 BLOCK-level overclaims.
