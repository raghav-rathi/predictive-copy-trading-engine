"""Hull Moving Average trend indicators (Alan Hull, 2005; causal, no lookahead).

HMA(n) = WMA(2*WMA(C, n/2) - WMA(C, n), sqrt(n))

The weighted moving average is implemented here because base.py has
no WMA. WMA weights the most recent bar most heavily (weights
1..n, normalised by n(n+1)/2), which is what lets the Hull average
react roughly twice as fast as an EMA of the same length while
staying smooth: the 2*WMA(n/2) - WMA(n) term over-weights recent
price, and the final WMA(sqrt(n)) smooths the overshoot back out.

Seeding (deterministic, causal): a WMA(n) is NaN until n bars have
been seen, so HMA(16) is first valid at bar 19 (16 bars for the
inner WMA(16) plus 4 bars for the outer WMA(4)) and HMA(64) at
bar 71. Before the first valid value each HMA column is seeded
with the bar's own close, so the indicator columns never contain
NaN. Seeding with the close is neutral for signals: C > HMA is
False when HMA == C, and the rising/falling test against the prior
seeded value is also False on a flat seed, so no setup can fire
before the averages are genuinely valid. The signal layer still
only sees boolean setup columns (no NaN by construction).

Columns:
    hma16, hma64, hma16_rising, hma16_falling,
    long_setup, short_setup, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

HMA_FAST = 16
HMA_SLOW = 64


def wma(s: pd.Series, n: int) -> pd.Series:
    """Weighted moving average, weights 1..n (most recent bar = n).

    NaN for the first n-1 bars (min_periods=n); purely causal.
    """
    w = np.arange(1, n + 1, dtype=float)
    return s.rolling(n, min_periods=n).apply(
        lambda x: float(np.dot(x, w) / w.sum()), raw=True
    )


def hull_ma(s: pd.Series, n: int) -> pd.Series:
    """Hull Moving Average: WMA(2*WMA(C, n/2) - WMA(C, n), sqrt(n))."""
    half = max(1, n // 2)
    root = max(1, int(round(n ** 0.5)))
    diff = 2 * wma(s, half) - wma(s, n)
    return wma(diff, root)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    hma16 = hull_ma(c, HMA_FAST)
    hma64 = hull_ma(c, HMA_SLOW)
    # Deterministic causal seeding: before the first valid value,
    # the average equals the bar's own close (never NaN, never a
    # future value; C > HMA is False there, so no setup can fire).
    df["hma16"] = hma16.fillna(c)
    df["hma64"] = hma64.fillna(c)
    df["atr"] = B.atr(h, l, c, 14)

    h16 = df["hma16"]
    rising = (h16 > h16.shift(1)).fillna(False)
    falling = (h16 < h16.shift(1)).fillna(False)
    df["hma16_rising"] = rising.astype(bool)
    df["hma16_falling"] = falling.astype(bool)

    df["long_setup"] = (
        (c > h16) & rising & (c > df["hma64"])
    ).astype(bool)
    df["short_setup"] = (
        (c < h16) & falling & (c < df["hma64"])
    ).astype(bool)
    return df
