"""Ehlers Instantaneous Trendline indicators (causal, no lookahead).

John Ehlers, Rocket Science for Traders (2001), chapter on the
Instantaneous Trendline. With alpha = 0.07:

    IT[i] = (a - a^2/4) * C[i] + 0.5 * a^2 * C[i-1]
          - (a - 0.75 * a^2) * C[i-2]
          + 2 * (1 - a) * IT[i-1] - (1 - a)^2 * IT[i-2]

The filter is a near-zero-lag trend extractor: a compact
recursive filter blending the last three closes with its own
prior outputs. Coefficients at alpha = 0.07:
a1 = 0.068775, a2 = 0.00245, a3 = 0.066325, b1 = 1.86, b2 = 0.8649.

Seeding (deterministic, documented): IT[0] = C[0], IT[1] = C[1]
(per the assigned spec; note the sibling strategy
ehlers_instantaneous_trendline seeds IT[1] as the mean of the
first two closes — the two specs differ here and this one
follows the task spec exactly). WARMUP = 30 bars is far longer
than the filter's settling time, so the seed has no effect on
traded bars.

Columns:
    it   -- the Instantaneous Trendline
    atr  -- Wilder ATR(14) for the risk layer

No lookahead: IT[i] uses closes through bar i and its own prior
values only.
"""

import numpy as np
import pandas as pd

ALPHA = 0.07


def instantaneous_trendline(c, alpha: float = ALPHA):
    """Return the Instantaneous Trendline series for a close series.

    Pure function; seeded IT[0] = C[0], IT[1] = C[1].
    """
    a = alpha
    a1 = a - a * a / 4.0
    a2 = 0.5 * a * a
    a3 = a - 0.75 * a * a
    b1 = 2.0 * (1.0 - a)
    b2 = (1.0 - a) ** 2
    cv = c.to_numpy(dtype=float)
    n = len(cv)
    it = np.zeros(n)
    if n == 0:
        return pd.Series(it, index=c.index, name="it")
    it[0] = cv[0]
    if n == 1:
        return pd.Series(it, index=c.index, name="it")
    it[1] = cv[1]
    for i in range(2, n):
        it[i] = (
            a1 * cv[i]
            + a2 * cv[i - 1]
            - a3 * cv[i - 2]
            + b1 * it[i - 1]
            - b2 * it[i - 2]
        )
    return pd.Series(it, index=c.index, name="it")


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    from strategies import base as B

    df = df.copy()
    df["it"] = instantaneous_trendline(df["c"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
