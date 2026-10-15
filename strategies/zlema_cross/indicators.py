"""Zero-Lag EMA indicators (de-lagged form).

ZLEMA[n]: lag = floor((n-1)/2); de-lagged series d[i] = c[i] + (c[i] -
c[i-lag]); ZLEMA = EMA(d, n). The construction extrapolates price
forward by the EMA's own lag and cancels it to first order.

Attribution note: this is the de-lagged form that ships as "zero lag"
in Tulip Indicators, pandas-ta, ta4j and TradingView Pine. Ehlers & Way's
original "Zero Lag (Well, Almost)" paper (S&C, Nov 2010) specifies a
*different* filter — an error-correcting EMA with a per-bar gain search —
so this implementation is the industry-standard de-lagged variant, not a
transcription of that paper.
"""

import pandas as pd

from strategies import base as B

FAST_N = 10
SLOW_N = 30


def _zlema(s: pd.Series, n: int) -> pd.Series:
    lag = (n - 1) // 2
    d = s + (s - s.shift(lag).fillna(s))
    return B.ema(d, n)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["zlema_fast"] = _zlema(df["c"], FAST_N)
    df["zlema_slow"] = _zlema(df["c"], SLOW_N)
    return df
