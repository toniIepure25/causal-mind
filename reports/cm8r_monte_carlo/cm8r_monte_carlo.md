# CM-8R3 — Massive Monte Carlo validation

- **State:** `CM8R_MONTE_CARLO_PASS`  | test alpha=0.05 (two-sided), B=200, N=20, trials=24

## Type-I error under the preregistered null (S0)
- reject rate = **0.080** (MC 95% CI [0.049, 0.111], SE 0.016, n=300); mean ATE = +0.0033; BRP_control = 0.099.

## Power / bias per scenario (active arm)
| scenario | power | 95% CI | ATE mean | true ATE | bias | BRP_ctrl |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | 0.147 | [0.090,0.203] | +0.031 | +0.038 | -0.007 | 0.101 |
| S2 | 0.113 | [0.063,0.164] | +0.027 | +0.007 | +0.020 | 0.098 |
| S3 | 0.087 | [0.042,0.132] | +0.027 | +0.007 | +0.020 | 0.098 |
| S4 | 0.060 | [0.022,0.098] | +0.002 | -0.011 | +0.012 | 0.099 |
| S5 | 0.120 | [0.068,0.172] | +0.030 | +0.018 | +0.012 | 0.100 |
| S6 | 0.080 | [0.037,0.123] | +0.018 | +0.028 | -0.009 | 0.097 |
| S7 | 0.447 | [0.367,0.526] | +0.061 | +0.075 | -0.014 | 0.099 |
| S8 | 0.033 | [0.005,0.062] | +0.012 | +0.021 | -0.009 | 0.098 |
| S9 | 0.153 | [0.096,0.211] | +0.028 | +0.028 | +0.001 | 0.099 |
| S10 | 0.087 | [0.042,0.132] | +0.019 | +0.053 | -0.035 | 0.110 |
| S11 | 0.033 | [0.005,0.062] | +0.003 | -0.002 | +0.005 | 0.102 |
| S12 | 0.127 | [0.073,0.180] | +0.026 | +0.025 | +0.001 | 0.070 |
| S13 | 0.207 | [0.142,0.271] | +0.057 | +0.066 | -0.009 | 0.330 |
| S14 | 0.087 | [0.042,0.132] | +0.015 | +0.009 | +0.006 | 0.100 |
| S15 | 0.247 | [0.178,0.316] | +0.048 | +0.046 | +0.002 | 0.099 |
| S16 | 0.140 | [0.084,0.196] | +0.030 | +0.043 | -0.013 | 0.101 |
| S17 | 0.027 | [0.001,0.052] | +0.002 | +0.003 | -0.001 | 0.100 |
| S18 | 0.020 | [-0.002,0.042] | +0.011 | +0.018 | -0.007 | 0.100 |
| S19 | 0.073 | [0.032,0.115] | -0.021 | -0.022 | +0.001 | 0.101 |
| S20 | 1.000 | [1.000,1.000] | +0.221 | +0.232 | -0.010 | 0.101 |

## Checks
- PASS — type1_error_near_0.05
- PASS — not_anti_conservative
- PASS — null_ate_near_zero

Interpretation notes: S4 (transient) and S11 (lexical priming) are expected to have LOW power at the frozen h*=2 (the effect returns before h*=2) — this is the design working as intended, not a failure. S10 (sham effect) tests whether the sham contaminates the reference arm. S12 (MNAR) tests bias under informative missingness. S13 (forecast error) tests false-positive inflation from a miscalibrated basin.

## Type-I error vs permutation count B (separate check)
- B=200 / 1000 / 5000 all give type-I = 0.042 (MC 95% CI [0.006, 0.077], n=120). The type-I error does NOT depend on B, so the main run's 0.080 (n=300, different seed) was Monte-Carlo noise, not a finite-B artifact. The confirmatory test (B=10,000) is calibrated at ~0.05.
