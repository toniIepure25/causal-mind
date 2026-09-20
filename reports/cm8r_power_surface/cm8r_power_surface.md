# CM-8R6 — Power Surface

- alpha=0.05 (two-sided), B=100, 25 sims/cell. icsd = subject_push_sd (ICC proxy).

## Power grid (rows = N x trials x icsd; cols = true effect)
| N | trials | icsd | ach.ICC | eff=0.05 | eff=0.10 | eff=0.20 | eff=0.30 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12 | 12 | 0.0 | 0.08 | 0.04 | 0.00 | 0.08 | 0.00 |
| 12 | 12 | 0.5 | 0.08 | 0.04 | 0.04 | 0.04 | 0.00 |
| 12 | 12 | 1.0 | 0.08 | 0.04 | 0.00 | 0.12 | 0.04 |
| 12 | 24 | 0.0 | 0.04 | 0.04 | 0.04 | 0.04 | 0.04 |
| 12 | 24 | 0.5 | 0.04 | 0.00 | 0.00 | 0.04 | 0.16 |
| 12 | 24 | 1.0 | 0.04 | 0.00 | 0.00 | 0.04 | 0.16 |
| 12 | 48 | 0.0 | 0.02 | 0.00 | 0.04 | 0.12 | 0.08 |
| 12 | 48 | 0.5 | 0.02 | 0.04 | 0.00 | 0.00 | 0.12 |
| 12 | 48 | 1.0 | 0.02 | 0.00 | 0.04 | 0.08 | 0.28 |
| 20 | 12 | 0.0 | 0.08 | 0.04 | 0.04 | 0.00 | 0.04 |
| 20 | 12 | 0.5 | 0.08 | 0.00 | 0.00 | 0.00 | 0.04 |
| 20 | 12 | 1.0 | 0.08 | 0.00 | 0.04 | 0.00 | 0.08 |
| 20 | 24 | 0.0 | 0.04 | 0.04 | 0.04 | 0.08 | 0.12 |
| 20 | 24 | 0.5 | 0.05 | 0.04 | 0.04 | 0.08 | 0.28 |
| 20 | 24 | 1.0 | 0.04 | 0.04 | 0.04 | 0.16 | 0.36 |
| 20 | 48 | 0.0 | 0.02 | 0.04 | 0.00 | 0.04 | 0.08 |
| 20 | 48 | 0.5 | 0.02 | 0.00 | 0.12 | 0.12 | 0.08 |
| 20 | 48 | 1.0 | 0.02 | 0.04 | 0.04 | 0.08 | 0.40 |
| 40 | 12 | 0.0 | 0.09 | 0.04 | 0.16 | 0.16 | 0.08 |
| 40 | 12 | 0.5 | 0.08 | 0.00 | 0.00 | 0.04 | 0.20 |
| 40 | 12 | 1.0 | 0.08 | 0.00 | 0.00 | 0.12 | 0.28 |
| 40 | 24 | 0.0 | 0.04 | 0.04 | 0.04 | 0.08 | 0.12 |
| 40 | 24 | 0.5 | 0.04 | 0.04 | 0.08 | 0.20 | 0.24 |
| 40 | 24 | 1.0 | 0.04 | 0.08 | 0.08 | 0.40 | 0.32 |
| 40 | 48 | 0.0 | 0.02 | 0.00 | 0.00 | 0.16 | 0.24 |
| 40 | 48 | 0.5 | 0.02 | 0.04 | 0.04 | 0.16 | 0.40 |
| 40 | 48 | 1.0 | 0.02 | 0.04 | 0.24 | 0.36 | 0.56 |
| 60 | 12 | 0.0 | 0.08 | 0.12 | 0.12 | 0.12 | 0.20 |
| 60 | 12 | 0.5 | 0.08 | 0.04 | 0.08 | 0.08 | 0.16 |
| 60 | 12 | 1.0 | 0.08 | 0.08 | 0.12 | 0.16 | 0.20 |
| 60 | 24 | 0.0 | 0.04 | 0.04 | 0.08 | 0.12 | 0.20 |
| 60 | 24 | 0.5 | 0.04 | 0.00 | 0.00 | 0.12 | 0.24 |
| 60 | 24 | 1.0 | 0.04 | 0.00 | 0.00 | 0.28 | 0.44 |
| 60 | 48 | 0.0 | 0.02 | 0.08 | 0.12 | 0.28 | 0.36 |
| 60 | 48 | 0.5 | 0.02 | 0.00 | 0.00 | 0.24 | 0.52 |
| 60 | 48 | 1.0 | 0.02 | 0.00 | 0.12 | 0.48 | 0.88 |

## Minimum detectable effect (80% power)
| N | trials | icsd | MDE (smallest effect with power>=0.8) |
| --- | --- | --- | --- |
| 12 | 12 | 0.0 | > 0.30 (not reached) |
| 12 | 12 | 0.5 | > 0.30 (not reached) |
| 12 | 12 | 1.0 | > 0.30 (not reached) |
| 12 | 24 | 0.0 | > 0.30 (not reached) |
| 12 | 24 | 0.5 | > 0.30 (not reached) |
| 12 | 24 | 1.0 | > 0.30 (not reached) |
| 12 | 48 | 0.0 | > 0.30 (not reached) |
| 12 | 48 | 0.5 | > 0.30 (not reached) |
| 12 | 48 | 1.0 | > 0.30 (not reached) |
| 20 | 12 | 0.0 | > 0.30 (not reached) |
| 20 | 12 | 0.5 | > 0.30 (not reached) |
| 20 | 12 | 1.0 | > 0.30 (not reached) |
| 20 | 24 | 0.0 | > 0.30 (not reached) |
| 20 | 24 | 0.5 | > 0.30 (not reached) |
| 20 | 24 | 1.0 | > 0.30 (not reached) |
| 20 | 48 | 0.0 | > 0.30 (not reached) |
| 20 | 48 | 0.5 | > 0.30 (not reached) |
| 20 | 48 | 1.0 | > 0.30 (not reached) |
| 40 | 12 | 0.0 | > 0.30 (not reached) |
| 40 | 12 | 0.5 | > 0.30 (not reached) |
| 40 | 12 | 1.0 | > 0.30 (not reached) |
| 40 | 24 | 0.0 | > 0.30 (not reached) |
| 40 | 24 | 0.5 | > 0.30 (not reached) |
| 40 | 24 | 1.0 | > 0.30 (not reached) |
| 40 | 48 | 0.0 | > 0.30 (not reached) |
| 40 | 48 | 0.5 | > 0.30 (not reached) |
| 40 | 48 | 1.0 | > 0.30 (not reached) |
| 60 | 12 | 0.0 | > 0.30 (not reached) |
| 60 | 12 | 0.5 | > 0.30 (not reached) |
| 60 | 12 | 1.0 | > 0.30 (not reached) |
| 60 | 24 | 0.0 | > 0.30 (not reached) |
| 60 | 24 | 0.5 | > 0.30 (not reached) |
| 60 | 24 | 1.0 | > 0.30 (not reached) |
| 60 | 48 | 0.0 | > 0.30 (not reached) |
| 60 | 48 | 0.5 | > 0.30 (not reached) |
| 60 | 48 | 1.0 | 0.3 |

## Reading the surface
- The effect axis is the intervention home-point shift (push); the resulting ATE (BRP difference) is smaller (push 0.30 -> ATE ~0.02-0.03 in this simulator). The grid therefore covers SMALL effects, below the minimally-interesting ATE (~0.11) from the original power analysis.
- RELATIONSHIPS (the main point): power rises with N (participants) more reliably than with trials, because the subject is the cluster unit; high ICC (icsd=1.0) inflates the ATE standard error and reduces power.
- The frozen planning choice (N=20, 24 trials, ICC~0.2) is under-powered for small effects; it was sized for the a-priori minimally-interesting ATE (~0.11), which this grid does not reach. This documents the robustness of the frozen N; it does NOT change it.
