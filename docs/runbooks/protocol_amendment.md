# Protocol Amendment Runbook

**Status:** canonical · **Audience:** orchestrator / causal / forecasting roles.

A **frozen protocol** (e.g. CM-2 split, CM-3 evaluation protocol, CM-8
confirmatory protocol) is sealed so results cannot be quietly changed. You may
**not** edit a frozen protocol in place. If the protocol must change, you make a
**protocol amendment** — a new, versioned, sealed protocol with a documented
reason — and you never reinterpret an existing result under the old protocol.

## When an amendment is required

- Changing the split, targets, horizons, metrics, baselines, nulls, or decision
  rule of a frozen protocol.
- Changing the interpretation of a frozen result (forbidden — see below).
- Adding a dataset to a frozen protocol's split.

## What is forbidden

- **Editing a frozen seal in place** (`cm2_split_seal.json`,
  `cm3_protocol_seal.json`, CM-8 config). The SHA-256 registry would no longer
  match and `cm artifacts verify` / invariants would fail.
- **Reinterpreting an existing result** to fit a new hypothesis (result
  shopping). A new question is a new experiment, not a reinterpretation.
- **Silently changing the decision rule** after outcomes are inspected.

## Amendment procedure

1. **Write the amendment doc** `docs/protocol/<name>_protocol_amendment_NNN.md`:
   - the exact delta from the prior protocol
   - the scientific reason (new evidence, new dataset, methodological fix)
   - what is unchanged (the invariant core)
   - the new decision rule, fixed **before** any new outcome is inspected
2. **Cut a new sealed protocol** (new seal hash), referencing the prior seal.
   The old seal remains valid for the results it already produced.
3. **Register the change:**
   - add the new protocol to `registries/` (lineage: old → new).
   - update `docs/current_state.md` and the changelog.
4. **Re-run the affected invariants** and `cm validate`. The old frozen results
   are untouched; new results use the new seal.
5. **Review.** The reviewer confirms the amendment is methodologically sound
   and not result shopping.

## Versioning

Amendments are numbered (`_amendment_001`, `_002`, …) and immutable once
sealed. A protocol's full history is the original + its amendment series. See
the existing example: `docs/protocol/cm2_protocol_amendment_001.md`.

## Checklist

- [ ] Amendment doc written (delta + reason + unchanged core + new decision rule)
- [ ] New sealed protocol cut (old seal preserved)
- [ ] Lineage registered (old → new)
- [ ] No existing result reinterpreted
- [ ] Invariants + `cm validate` pass
- [ ] Reviewer sign-off recorded
- [ ] Changelog + `docs/current_state.md` updated
