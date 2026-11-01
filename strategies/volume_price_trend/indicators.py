"""Volume Price Trend indicators (PVT).

Unlike OBV, which adds or subtracts the whole bar volume on the sign
of the move, PVT scales volume by the size of the percentage move: a
2% advance on heavy volume moves PVT far more than a 0.1% drift on the
same volume. The series is cumulative, so only its direction and its
crosses of a smoothed average carry information.

Columns:
    vpt     -- cumulative sum of volume * percentage price change
    vpt_avg -- SMA(20) of PVT, the signal line
    atr     -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import pandas as pd

from strategies import base as B

AVG_PERIOD = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pct = df["c"].pct_change().fillna(0.0)
    df["vpt"] = (df["v"] * pct).cumsum()
    df["vpt_avg"] = B.sma(df["vpt"], AVG_PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
