"""Next-thought forecasting baselines (ladder B0-B5).

The baseline ladder defines the bar that any learned model must beat before
we claim it captures structure in the thought stream. Each rung adds one
assumption about how much history matters:

- B0 (marginal): the next thought category is drawn from the empirical
  marginal distribution, ignoring all history. Implemented here as
  :func:`b0_marginal`.
- B1 (previous state): the next category equals the current (last) category,
  i.e. a first-order "stay put" model. Implemented here as :func:`b1_previous`.
- B2 (n-gram): the next category depends on the last n observed categories
  (higher-order Markov chain). Not yet implemented.
- B3 (session-aware): history is truncated at session boundaries; transitions
  are estimated within sessions. Not yet implemented.
- B4 (linear probe): a linear classifier over a frozen semantic embedding of
  the recent window. Not yet implemented.
- B5 (sequence model): a recurrent/transformer model over the full window.
  Not yet implemented.

All baselines are pure Python and operate on category labels (strings) so
they can be evaluated before any representation or neural machinery exists.
"""

from __future__ import annotations


def b0_marginal(categories: list[str]) -> dict[str, float]:
    """Return the empirical marginal distribution over categories.

    Args:
        categories: Observed category labels, in temporal order.

    Returns:
        A mapping from each observed category to its relative frequency.
        The values sum to 1.0 (up to floating point). An empty input yields
        an empty distribution.
    """
    counts: dict[str, int] = {}
    for category in categories:
        counts[category] = counts.get(category, 0) + 1
    total = len(categories)
    if total == 0:
        return {}
    return {category: count / total for category, count in counts.items()}


def b1_previous(categories: list[str]) -> str | None:
    """Predict the next category as the current (last) category.

    Args:
        categories: Observed category labels, in temporal order.

    Returns:
        The last observed category, or ``None`` if the input is empty.
    """
    if not categories:
        return None
    return categories[-1]
