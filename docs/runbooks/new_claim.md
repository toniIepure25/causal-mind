# New Claim Runbook

**Status:** canonical · **Audience:** any role registering a claim.

A **claim** is a single, checkable scientific statement registered in
`claims/claims.json` at an explicit **level (0-8)**. The level is the claim's
honest strength; a lower-level result is never worded as a higher-level one.

## The level scale (0-8)

| Level | Meaning |
|-------|---------|
| 0 | Reproducibility / integrity only (e.g. "the frozen forecaster re-fits bit-identically"). |
| 1 | Descriptive / data-integrity finding. |
| 2 | Association on a single dataset, no controls. |
| 3 | Association that survives basic controls (e.g. a sealed held-out split). |
| 4 | Association with uncertainty + negative controls. |
| 5 | Robust effect: beats baselines, CIs exclude 0, nulls survive. |
| 6 | Method validated (the *procedure* is sound), effect may be null. |
| 7 | Causal claim with an identification strategy that actually identifies. |
| 8 | Causal claim with a confirmed intervention effect (replicated). |

**Never inflate.** If the evidence supports L4, register L4. The claim linter
(`data/scripts/cm_pub_claim_linter.py`) flags overclaiming language.

## Steps

1. **Write the claim** as one checkable sentence.
2. **Assign the level** using the scale above. When in doubt, go lower.
3. **Add it to `claims/claims.json`** with all required fields:
   ```json
   {
     "id": "C-1XX",
     "level": 5,
     "claim": "<one checkable sentence>",
     "status": "validated | null | partial | negative",
     "dataset": "<dataset id>",
     "protocol": "<protocol id / seal>",
     "script": "data/scripts/<name>.py",
     "report": "reports/<name>/<name>.md",
     "statistic": "<point estimate + CI + p>",
     "commit": "<git sha that produced it>",
     "reproduction": "cm reproduce <name>",
     "red_team": "<reviewer sign-off ref>"
   }
   ```
4. **Verify the graph:**
   ```bash
   cm claims verify        # schema + traceability (script/report/commit exist)
   ```
5. **Update the evidence matrix** (`docs/claims/evidence_matrix.md`) and
   `docs/current_state.md`.

## Rules

- **Append-only.** Do not edit a registered claim's level/statistic to make it
  look stronger. If the evidence changes, add a new claim and mark the old one
  `superseded`.
- **Every field must resolve.** `script`, `report`, and `commit` must exist;
  `cm claims verify` checks this.
- **Red-team required.** A claim is not "validated" until the reviewer's leakage
  audit passes (`red_team` field).
- **Negative results are claims.** Register a null/negative at its true level.

## Checklist

- [ ] One checkable sentence
- [ ] Honest level (0-8), not inflated
- [ ] All required fields present and resolvable
- [ ] `cm claims verify` PASS
- [ ] Evidence matrix + `docs/current_state.md` updated
- [ ] Reviewer red-team sign-off recorded
