# CM-8R7 — BRP Adversarial Red Team

- 9 adversarial cases; 7 produce a misleading 'success' (high BRP, no real redirection).

| case | BRP | cos-dir | Mahalanobis | persist | novelty | misleading |
| --- | --- | --- | --- | --- | --- | --- |
| epsilon_crossing | 1.00 | 0.000 | 6.95 | 10 | 12.50 | YES |
| anisotropic | 0.50 | 1.000 | 6.54 | 3 | 6.51 | no |
| high_dim_concentration | 1.00 | 1.000 | 17.16 | 10 | 17.01 | YES |
| lexical_repetition | 1.00 | 1.148 | 9.06 | 10 | 6.23 | YES |
| magnitude_change | 1.00 | 0.000 | 13.71 | 10 | 18.13 | YES |
| noisy_forecast_tiny_basin | 1.00 | 0.288 | 5.67 | 10 | 8.04 | YES |
| volatile_participant | 1.00 | 1.027 | 12.86 | 10 | 11.34 | YES |
| encoder_instability | 1.00 | 0.604 | 8.25 | 10 | 8.96 | YES |
| one_unusual_thought | 0.10 | 0.083 | 2.81 | 1 | 6.39 | no |

## Failure modes and the diagnostic that catches each
- **epsilon_crossing** (BRP=1.00): Trajectory hovers just outside the radius (5% over) with no directional shift. BRP ~1.0 but the semantic change is tiny.
- **anisotropic** (BRP=0.50): Embedding distribution is anisotropic (stretched). A ball basin is a poor fit; Mahalanobis distance (which uses the covariance) disagrees with the Euclidean BRP.
- **high_dim_concentration** (BRP=1.00): In high dimensions the points concentrate on a large sphere; the Euclidean radius is dominated by dimension, not semantics. Angular deviation is the right measure here.
- **lexical_repetition** (BRP=1.00): The participant repeats the cue word (all states near the cue). BRP is high (far from the predicted basin) but it is a lexical echo, not a semantic branch change. Persistence + novelty diagnostics reveal it.
- **magnitude_change** (BRP=1.00): Embedding magnitude doubles but the direction is unchanged. Euclidean BRP is high, but cosine-direction change ~0 shows no semantic redirection.
- **noisy_forecast_tiny_basin** (BRP=1.00): A noisy forecast produces an abnormally small basin radius; nearly everything falls outside -> spuriously high BRP. The radius itself is the red flag.
- **volatile_participant** (BRP=1.00): A naturally volatile participant jumps between topics; BRP is high even without an intervention. The CONTROL BRP would also be high (the ATE, not the raw BRP, is the estimand).
- **encoder_instability** (BRP=1.00): Semantic-encoder instability makes the embeddings drift; BRP is miscalibrated. The CONTROL BRP would be off too (calibration check catches this).
- **one_unusual_thought** (BRP=0.10): A single unusual thought creates an apparent branch change. BRP is elevated but persistence is low (it returns) -> not a durable redirection.

## Conclusion

The frozen BRP is a valid PRIMARY estimand but has known failure modes (magnitude-only change, lexical echo, tiny-basin miscalibration, volatility). The secondary diagnostics (cosine-direction change, Mahalanobis, persistence, novelty) reveal these modes. The frozen BRP is NOT replaced; these diagnostics are pre-declared SECONDARY robustness analyses. The ATE (intervention vs control BRP), not the raw BRP, is the estimand, which guards against volatility/encoder miscalibration.
