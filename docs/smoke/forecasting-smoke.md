# Smoke: Forecasting Baselines B0/B1

`src/causal_mind/forecasting/baselines.py` implements the first two rungs of
the next-thought baseline ladder (B0-B5), in pure Python with type hints.

- `b0_marginal(categories: list[str]) -> dict[str, float]` — the empirical
  marginal distribution over categories (relative frequencies, summing to 1).
  Empty input returns `{}`.
- `b1_previous(categories: list[str]) -> str | None` — predicts the next
  category as the last observed category. Empty input returns `None`.

The module docstring documents the full ladder: B0 marginal, B1 previous
state, B2 n-gram, B3 session-aware, B4 linear probe over frozen embeddings,
B5 sequence model. B2-B5 are stubs to be added as validation evidence
justifies them. These baselines set the bar any learned model must beat.

Verified: `python -m pytest tests/test_task_queue.py -q` passes from the
worktree.
