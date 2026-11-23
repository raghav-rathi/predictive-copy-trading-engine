"""Tillson T3 indicators (Tim Tillson, 1998; causal, no lookahead).

T3(n, v) = c1*e6 + c2*e5 + c3*e4 + c4*e3, where e1..e6 are six
successive EMAs of the close with period n, and (v = vfactor):

    c1 = -v^3
    c2 =  3v^2 + 3v^3
    c3 = -6v^2 - 3v - 3v^3
    c4 =  1 + 3v + v^3 + 3v^2

The coefficients sum to 1, so T3 of a constant series is that
constant. The six-EMA stack with these weights is a lag-reduced
smoother: it tracks price far more closely than a single EMA of
the same period while removing more noise than a raw EMA — it is
a better EMA, not a new indicator family.

Seeding (deterministic, causal): each EMA is seeded at the first
close (pandas ewm with min_periods=1, adjust=False), exactly as
in the standard Tillson implementation — the first EMA value is
the first close, so e1..e6 and T3 are defined from bar 0 with no
lookahead and no NaN anywhere. Early bars carry a warm-up bias
(the stack has not yet "seen" a full period), which is why the
strategy's WARMUP is 60 bars; no setup can fire on a flat seed
anyway, since C > T3 is False when T3 == C and the rising test
against the prior seeded value is False on a flat series.

Columns:
    t3_fast, t3_slow, t3_rising, t3_falling,
    long_setup, short_setup, atr
"""

import pandas as pd

from strategies import base as B

T3_FAST_N = 10
T3_FAST_V = 0.7
T3_SLOW_N = 30
T3_SLOW_V = 0.7


def _ema(s: pd.Series, n: int) -> pd.Series:
    """EMA seeded at the first value (min_periods=1), causal."""
    return s.ewm(span=n, adjust=False, min_periods=1).mean()


def tillson_t3(s: pd.Series, n: int = 10, vfactor: float = 0.7) -> pd.Series:
    """Tillson T3: six successive EMAs combined with the Tillson weights."""
    e1 = _ema(s, n)
    e2 = _ema(e1, n)
    e3 = _ema(e2, n)
    e4 = _ema(e3, n)
    e5 = _ema(e4, n)
    e6 = _ema(e5, n)
    v = vfactor
    c1 = -(v ** 3)
    c2 = 3 * v ** 2 + 3 * v ** 3
    c3 = -6 * v ** 2 - 3 * v - 3 * v ** 3
    c4 = 1 + 3 * v + v ** 3 + 3 * v ** 2
    return c1 * e6 + c2 * e5 + c3 * e4 + c4 * e3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    df["t3_fast"] = tillson_t3(c, T3_FAST_N, T3_FAST_V)
    df["t3_slow"] = tillson_t3(c, T3_SLOW_N, T3_SLOW_V)
    df["atr"] = B.atr(h, l, c, 14)

    t3 = df["t3_fast"]
    rising = (t3 > t3.shift(1)).fillna(False)
    falling = (t3 < t3.shift(1)).fillna(False)
    df["t3_rising"] = rising.astype(bool)
    df["t3_falling"] = falling.astype(bool)

    df["long_setup"] = (
        (c > t3) & rising & (t3 > df["t3_slow"])
    ).astype(bool)
    df["short_setup"] = (
        (c < t3) & falling & (t3 < df["t3_slow"])
    ).astype(bool)
    return df
