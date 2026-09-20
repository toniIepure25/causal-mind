# CM-8R11 — Latency Benchmark

- 24 trials; local frozen artifacts (no Qwen / no internet).

## Per-stage latency (ms)
| stage | p50 | p90 | p95 | p99 | max |
| --- | --- | --- | --- | --- | --- |
| encode | 97.161 | 99.099 | 102.087 | 172.527 | 193.423 |
| predict | 0.435 | 0.527 | 0.638 | 72.889 | 94.464 |
| randomize | 0.011 | 0.015 | 0.016 | 0.016 | 0.016 |
| render | 0.005 | 0.006 | 0.006 | 0.006 | 0.006 |
| post_encode | 203.509 | 294.483 | 295.81 | 296.585 | 296.77 |
| brp | 1.957 | 2.422 | 76.67 | 389.58 | 479.135 |
| total | 303.378 | 395.285 | 478.04 | 788.228 | 876.542 |

## Cold (first trial after model load), ms
| stage | cold ms |
| --- | --- |
| encode | 99.344 |
| predict | 94.464 |
| randomize | 0.013 |
| render | 0.006 |
| post_encode | 203.572 |
| brp | 479.135 |
| total | 876.542 |

Latency is LOCAL (frozen MiniLM encoder + ridge forecaster). The participant-facing critical path is encode + predict + render + BRP. No Qwen / no LLM API / no internet in the loop.
