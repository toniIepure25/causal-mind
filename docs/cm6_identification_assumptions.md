# CM-6A — Identification Assumptions

Generated: 2026-09-16 · Engine: CAUSAL/STATS (CM-6A).
Companion to `docs/cm6_candidate_causal_graph.md` and `reports/cm6_candidate_scm.json`.

This document states, for the candidate dynamic cognitive SCM, **exactly which
identification assumptions are required, which hold, and which fail** in ds006067. It is the
audit trail for the claim that **0 / 84 candidate edges are causally identifiable** from the
observational data.

## 1. Target estimand

For a candidate edge `X[t] -> Y[t+1]` (e.g. `joy[t] -> joy[t+1]`), the target is the
**causal effect** of setting `X[t] = a` versus `X[t] = b` on the distribution of `Y[t+1]`:

```
P( Y[t+1] | do( X[t] = a ),  history )      vs      P( Y[t+1] | do( X[t] = b ),  history )
```

This is a **local, one-step, interventional** estimand. It is *not* the observational
association `P( Y[t+1] | X[t] = a, history )`.

## 2. Assumptions required to identify it from observational data

To identify the estimand by **backdoor adjustment** (the only route available without
randomization), all of the following must hold:

| # | Assumption | Formal statement | Holds in ds006067? |
| --- | --- | --- | --- |
| A1 | **Temporal precedence** | `X` is measured at `t`, `Y` at `t+1`; no reverse-time path | **Yes** (by construction; events are time-ordered) |
| A2 | **Confounder measurement** | All common causes of `X[t]` and `Y[t+1]` are measured | **No** — `latent_U[t]` (trait, mood baseline, engagement, unmodeled stimulus features) is a common cause and is **not measured** |
| A3 | **Ignorability / no unmeasured confounding** | `Y[t+1] ⫫ X[t] | do-adjustment set` | **No** — fails because of A2 |
| A4 | **Positivity / overlap** | `0 < P(X[t]=a | adjustment) < 1` | Partially — holds for common values, not guaranteed for rare category values |
| A5 | **Consistency / no interference** | the observed `Y` under `X=a` equals the counterfactual under `do(X=a)`; no unit-level interference | Assumed (single participant, no interference) — **Yes** |
| A6 | **Stationarity** | the transition law is stable within the scan | Assumed (~10 min scan) — **Approximately** |
| A7 | **Correct graph** | the SCM's edge set is the true causal graph | **Unknown** — the graph is a *candidate*; edges are not validated |

**The decisive failure is A2/A3.** Because `latent_U[t]` is an unmeasured common cause of
every measured dimension, **no adjustment set can block the backdoor path**
`X[t] <- latent_U[t] -> Y[t+1]`. Conditioning on a measured descendant of `latent_U` would
introduce collider bias, not remove confounding. Hence the backdoor criterion is
unsatisfiable and the one-step causal effect is **not identifiable**.

## 3. What the identifiability audit actually checked

For each of the 84 candidate edges `X[t] -> Y[t+1]`, the audit:

1. Built the SCM DAG (measured nodes at `t` and `t+1`, plus `latent_U[t]`).
2. Enumerated backdoor paths between `X[t]` and `Y[t+1]`.
3. Searched for an adjustment set that (i) blocks all backdoor paths, (ii) contains no
   descendant of `X[t]`, and (iii) uses only **observed** nodes.
4. Result: for **every** edge, every blocking set requires `latent_U[t]` (unobserved) →
   **status = NOT IDENTIFIABLE**, `adjustment_set = null`.

This is implemented and unit-tested in `src/causal_mind/causal/identifiability.py`
(`backdoor_adjustment_set`, `audit_edge_identifiability`) and exercised on a synthetic DAG
where a *measured* confounder makes the edge identifiable (the test confirms the method
returns identifiable when it should).

## 4. Under what conditions WOULD an edge become identifiable?

An edge `X[t] -> Y[t+1]` becomes **CAUSALLY IDENTIFIED** if any of these holds:

- **R1 — Randomization of X.** `X[t]` is assigned (subject-, trial-, or block-level)
  independently of `latent_U[t]`. Then the backdoor path is broken by design and
  `P(Y[t+1] | do(X=a)) = P(Y[t+1] | X=a)`. **This is what an experiment (CM-6F) or a
  randomized public dataset (CM-6B, e.g. ds005494) provides.**
- **R2 — Measured confounders.** If `latent_U[t]` were measured (e.g. a validated mood
  baseline + trait + engagement measure at `t`), backdoor adjustment on it would identify
  the effect. ds006067 does not collect a per-thought mood baseline.
- **R3 — Instrumental variable / front-door.** A valid instrument for `X[t]` or a front-door
  path through a measured mediator. None is available in ds006067.
- **R4 — Natural experiment / regression discontinuity.** A plausibly exogenous shock to
  `X[t]`. Not present in the think-aloud design.

**None of R1–R4 hold in ds006067.** Therefore the honest, frozen conclusion is:
**the observational data cannot identify any one-step causal effect; it can only rank
candidate antecedents for perturbation.**

## 5. Consequences for claims

- Every CM-6A edge label is capped at **CONDITIONALLY SUPPORTED** (or
  TEMPORALLY PRECEDENT / ASSOCIATIONAL). **No edge may be labeled CAUSALLY IDENTIFIED**
  without R1–R4 evidence. The code enforces this: `counterfactuals.py` refuses to emit
  `experimentally_identified` status without an attached randomized-evidence record.
- The **predictive** findings (lagged skill, conditional dependence, incremental value,
  stability) are valid **L1–L5** claims and are reported as such. They are *not* causal.
- The transition to **L6 (causal evidence)** requires CM-6B (a randomized public dataset) or
  CM-6F (our own randomized experiment). Until then, the project's causal claims are
  **designs and identifiability arguments, not measured causal effects.**

## 6. Anti-HARKing / freeze note

The candidate graph, the 7 analyses, the edge-label taxonomy, and this identification
account are **frozen as of commit f3348dc (CM-6 baseline)**. Any change to the SCM node/edge set, the
assumptions, or the identifiability method after seeing downstream experiment outcomes
requires a new ADR + research-log entry and must not be used to retrofit a causal claim.
