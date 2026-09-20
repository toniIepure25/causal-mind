# The Synthetic Oracle Lab: A Theory of Prediction vs. Intervention (Outline)

**Outline (CM-9A → CM-9).** Status: synthetic exploration, `CM9A_SYNTHETIC_ORACLE_READY`,
part of the `cm8-prehuman-v1.0` freeze. **No claim about real human thought; no free-will
claim.** This is a separate research direction from the CM-8 confirmatory experiment.

---

## 1. The question

When an **oracle** intervenes on an agent's thought stream, how does that intervention change
the agent's ability to **predict its own future**? We formalize this with two metrics and
study it in a synthetic world where the ground truth is known.

## 2. The synthetic world

- **Agent:** a mean-reverting thought stream (a controllable dynamical system with known
  parameters).
- **Oracle:** an external agent that intervenes in **4 conditions**:
  - **HIDDEN** — the oracle intervenes without the agent knowing.
  - **REVEAL** — the oracle reveals its intervention to the agent.
  - **VETO** — the oracle can veto (block) the agent's next state.
  - **REDIRECT** — the oracle redirects the agent's next state.
- **Agent policies (O0–O10):** 11 policies the agent can use to predict/act, including
  computational-irreducibility (O10) and game-theoretic best-response (O7) probes.
- **Scale:** 300 steps × 20 seeds; baseline self-prediction error 3.93.

## 3. The metrics

- **RPR (Relative Prediction Ratio):** the ratio of the agent's self-prediction error
  **with** the oracle's intervention to its error **without**. RPR > 1 means the
  intervention makes the future *less* predictable; RPR < 1 means *more* predictable.
- **PIE (Prediction–Intervention Effect):** the absolute change in self-prediction error
  induced by the intervention.

## 4. Key synthetic results

- **HIDDEN + O5** is the **least** predictable (RPR = **1.48**): a hidden intervention by a
  particular policy maximally disrupts the agent's self-prediction.
- **VETO + O0** is the **most** predictable (RPR = **0.16**): a veto under a baseline policy
  makes the future highly predictable (the agent can anticipate the block).
- The RPR/PIE surface over the 4 conditions × 11 policies characterizes **when an oracle's
  intervention is detectable** in the agent's self-prediction.

## 5. The theoretical program (CM-9)

1. **Characterize detectability.** Derive, for each oracle condition and agent policy, when
   the intervention is detectable (RPR deviates from 1) and when it is hidden (RPR ≈ 1).
2. **Computational irreducibility (O10).** Study the limit where the agent's best policy is
   computationally irreducible — the intervention is undetectable without simulating the
   future.
3. **Game-theoretic best response (O7).** Study the equilibrium where the agent and oracle
   best-respond to each other; characterize the RPR/PIE at equilibrium.
4. **Connection to the empirical program.** Use the synthetic theory to (a) choose which
   interventions are *detectable* in the CM-8 experiment, and (b) interpret the BRP as a
   measure of how much an intervention moves the future out of the predicted basin.

## 6. Scope and claims

- **Synthetic only.** No claim about real human thought; the agent is a mean-reverting
  system with known parameters.
- **No free-will claim.** The oracle is a formal object; the lab studies prediction vs.
  intervention, not consciousness.
- **Ready state:** `CM9A_SYNTHETIC_ORACLE_READY` (the lab runs; the metrics are measured;
  the probes are in place). The theory (CM-9) is the next step.

## 7. Deliverables

- `src/causal_mind/oracle/` — the synthetic world, oracle conditions, agent policies, RPR/PIE.
- `data/scripts/cm9a_oracle_lab.py` — the lab runner.
- `reports/cm9a_oracle_lab/cm9a_oracle_lab.json` — the measured RPR/PIE surface.
- This outline — the theoretical program (CM-9).
