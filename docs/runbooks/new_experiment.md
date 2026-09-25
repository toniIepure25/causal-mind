# New Experiment Runbook

**Status:** canonical · **Audience:** forecasting / causal / researcher roles.

An **experiment** is a reproducible procedure that produces a scientific result
and a registered claim. This runbook is the checklist that keeps a new
experiment honest and reproducible.

## 0. Before you start

- Read `docs/current_state.md` — is this already done? Is it a reinterpretation
  of an existing result (forbidden) or a new question (allowed)?
- Confirm the data exists and is lawfully usable ([new dataset runbook](new_dataset.md)).
- If the experiment touches a **frozen protocol**, you need a
  [protocol amendment](protocol_amendment.md) first.

## 1. Freeze the protocol (before touching outcomes)

- Write the protocol: split, targets, horizons, metrics, baselines, nulls,
  decision rule. Put it in `docs/protocol/<name>_frozen_protocol.md`.
- **Seal it** (a hash persisted to disk so it cannot be quietly changed), like
  `data/manifests/cm3_protocol_seal.json`.
- The decision rule (what counts as PASS/NULL/FAIL) is fixed **now**, before
  any result is inspected.

## 2. Implement

- Reuse the library (`src/causal_mind`); put reusable logic there, not in the
  script. The script in `data/scripts/<name>.py` orchestrates and writes the
  report.
- Use `causal_mind.constants` for all scientific constants (read from frozen
  configs). Use `causal_mind.paths` for all paths.
- Seed every RNG. Record the seed in the run manifest.
- Assign a **run ID** (`causal_mind.runid.make_run_id`) and write it into the
  output manifest so the result traces to (git SHA, timestamp, seed).

## 3. Validate (the non-negotiables)

- **Subject-disjoint** split only; never random rows on temporal data.
- **Uncertainty** on every headline number: bootstrap CIs, permutation test,
  effect size.
- **Negative controls**: label/permutation/shuffle controls that should be null.
- **Baselines**: the model must beat the frozen baseline ladder
  (`src/causal_mind/forecast/baselines.py`).
- **Leakage audit**: run `data/scripts/cm_leakage_scan.py`; the reviewer must
  sign off before the result is "validated".

## 4. Report + register

- Write `reports/<name>/<name>.md` + a machine-readable `<name>.json`.
- Register the **claim** at an honest level (0-8) — see
  [new claim runbook](new_claim.md). A negative result is a result; register it
  at its true level, never inflated.
- Add the experiment to `experiments/experiment_registry.json` and
  `registries/lineage.json`.
- Update `docs/current_state.md`.

## 5. Verify + reproduce

```bash
cm validate               # invariants + leakage + security + claims
# make the experiment reproducible by name:
#   add it to _REPRODUCE in src/causal_mind/cli_research.py
cm reproduce <name>       # re-runs the experiment end-to-end
```

## 6. Update threat models

If the experiment introduces a new data source, data class, or network path,
update the relevant table in
[threat models](../governance/threat_models.md).

## Checklist

- [ ] Protocol written + sealed **before** outcomes inspected
- [ ] Decision rule fixed in advance
- [ ] Subject-disjoint split; seeded RNG; run ID recorded
- [ ] Uncertainty + negative controls + baselines
- [ ] Leakage scan PASS + reviewer sign-off
- [ ] Report (md + json) written
- [ ] Claim registered at an honest level
- [ ] Experiment + lineage registered
- [ ] `cm validate` PASS; `cm reproduce <name>` works
- [ ] `docs/current_state.md` updated
