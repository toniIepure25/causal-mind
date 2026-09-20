# Paper 1 — Figure Specifications

One master figure set for the predictive-dynamics paper. Each figure lists the exact data
source (committed report), what it shows, and the generation command. All figures are
generated from frozen artifacts; no new analysis.

## Figure 1 — The thought stream and the forecast

- **What:** A schematic of one subject's thought stream: a sequence of thought embeddings,
  a k≈3 history window, and the multi-horizon forecast (h=1..10) with the predicted-future
  basin.
- **Source:** schematic (no data). Annotate with the frozen forecaster
  (`LinearMultiHorizon`, k=3, α=100) and the basin (90th-pct held-out error norm).
- **Purpose:** orient the reader to the setup.

## Figure 2 — Next-thought prediction vs. baselines (L3)

- **What:** Bar/point plot of held-out semantic cosine for the model vs. baselines B0–B7,
  with 95% CIs. Model **0.3623 [0.3523, 0.3720]**; strongest baseline B0 **0.3167
  [0.3078, 0.3250]**; non-overlapping CIs.
- **Source:** `reports/cm2_results.json` (`main_model.test_sem_ci`, `baselines.*`).
- **Generation:** `.venv/bin/python data/scripts/cm8r_analysis.py --figure=cm2_baselines`
  (or a small plotting script reading the JSON).
- **Note:** label the permutation null (p=0.0000) in the caption.

## Figure 3 — Multi-horizon gain with smooth decay (L5, the key figure)

- **What:** The gain over the strongest horizon-specific baseline vs. horizon h=1..10,
  with 95% CIs. Show the **smooth monotonic decay** (+0.0349 at h=1 → +0.0044 at h=10).
  Optionally overlay the model and strongest-baseline curves.
- **Source:** `reports/cm3_results.json` (`FPC_semantic.<h>.model`, `.strong_baseline_ci`,
  `.gain`).
- **Generation:** `.venv/bin/python data/scripts/cm8r_analysis.py --figure=cm3_horizons`.
- **Note:** this is the central result; the decay shape is the qualitative claim.

## Figure 4 — Thought Predictive Horizon (TPH)

- **What:** The horizon at which the gain's CI crosses zero (here, beyond h=10, so the TPH
  is **≥ 10 thoughts / ~2 minutes**, a lower bound). Plot gain vs. horizon with the zero
  line and the h=10 lower-bound marker.
- **Source:** `reports/cm3_results.json`.
- **Note:** state explicitly that this is a **lower bound** (the gain is still significant
  at the max tested horizon).

## Figure 5 — Null robustness (optional / supplement)

- **What:** The multi-horizon gain under (a) the real data, (b) time-shuffled history,
  (c) transition-destroyed history, (d) random-target null. Real data shows the decay; the
  nulls collapse to ~0 (p=0.0000).
- **Source:** the CM-3 null runs (see `reports/cm3_results.json` and the CM-3 protocol).
- **Purpose:** rule out that the gain is an artifact of the data's temporal structure.

## Figure 6 — Predicted-future basin (optional / supplement)

- **What:** A 2-D projection (PCA) of the frozen forecast, the basin ball (radius = 90th-
  pct held-out error norm), and the held-out natural futures (BRP_control ≈ 0.0785, i.e.,
  ~7.85% outside the basin, close to the 0.10 target).
- **Source:** `reports/cm8r_ghost_pilot/cm8r_ghost_pilot.json` (BRP_control held-out TEST).
- **Purpose:** connect the prediction to the intervention estimand (BRP) used in Paper 2.

## Style

- Consistent palette; semantic cosine on the y-axis for Figs 2–4; CIs as error bars.
- Every figure caption states the exact split (83/18/17 sealed), the metric (semantic
  cosine), and that no causal/free-will claim is made.
- Reproducible: every figure is generated from a committed report by a committed script.
