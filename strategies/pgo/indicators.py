"""Mark Johnson's Pretty Good Oscillator (PGO) indicators.

PGO measures how far the close has stretched from its N-bar simple
moving average, in units of average true range:

    PGO = (C - SMA(C, N)) / EMA(TR, N)

It is a volatility-normalized momentum gauge: +1 means price sits one
ATR above its mean (strong thrust), -1 the mirror. Breakout entries on
+/-1 crosses ride volatility-adjusted momentum; exits back at the zero
line take profit when the stretch mean-reverts. All causal: only data
through bar i's close.
"""

import pandas as pd

from strategies import base as B

N = 14
ENTRY_LEVEL = 1.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dist = df["c"] - B.sma(df["c"], N)
    vol = B.atr(df["h"], df["l"], df["c"], N)
    df["pgo"] = dist / vol.replace(0, float("nan"))
    return df
