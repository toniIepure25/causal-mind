# CM-9A — Synthetic Oracle Lab

- **State:** `CM9A_SYNTHETIC_ORACLE_READY`  | 300 steps x 20 seeds
- **Baseline self-prediction error (no oracle):** 3.927

## RPR grid (oracle self-pred-error / baseline; <1 = more predictable)
| condition | O0 | O1 | O2 | O3 | O4 | O5 | O6 | O7 | O8 | O9 | O10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hidden | 1.06 | 1.06 | 1.06 | 1.06 | 1.06 | 1.48 | 1.06 | 1.06 | 1.06 | 1.06 | 1.11 |
| reveal | 1.06 | 1.06 | 1.13 | 1.08 | 1.10 | 1.48 | 1.13 | 1.06 | 1.06 | 1.06 | 1.13 |
| veto | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 | 0.16 |
| redirect | 0.41 | 0.41 | 0.50 | 0.43 | 0.47 | 1.02 | 0.50 | 0.45 | 0.41 | 0.41 | 0.71 |

## Most / least predictable (condition, policy)
- most predictable (lowest RPR): {'condition': 'veto', 'policy': 'O0', 'rpr': 0.15837364577974122, 'pie': -3.3048553141154233}
- least predictable (highest RPR): {'condition': 'hidden', 'policy': 'O5', 'rpr': 1.483065641185052, 'pie': 1.8968774484445268}

## Computational irreducibility probe

O10's response is a nonlinear (tanh + sin + quadratic) function of the state; a linear projection captures only part of it. This is a computational-irreducibility probe (the response cannot be reduced to a simple linear rule).

## Game-theoretic probe

O7 plays a best response to the revealed shift (0.7*signal - 0.1*x). This is a one-shot best response; in the synthetic lab it is stable because the oracle's shift is i.i.d. (no strategic feedback loop).

## Conclusion

The synthetic Oracle lab is ready. For each of the 4 oracle conditions (HIDDEN/REVEAL/VETO/REDIRECT) and 11 agent policies (O0-O10), the lab measures how the oracle's intervention changes the agent's ability to predict its own future (RPR, PIE). REDIRECT/VETO make the future MORE predictable (RPR < 1); HIDDEN random shifts make it LESS predictable (RPR > 1). The probes address computational irreducibility (O10) and game-theoretic best response (O7). This is a synthetic exploration; it does not touch the frozen CM-8 confirmatory experiment.
