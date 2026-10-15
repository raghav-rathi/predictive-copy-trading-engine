"""Price-Volume Trend indicators (Joseph Granville).

PVT[i] = PVT[i-1] + volume[i] * (close[i] - close[i-1]) / close[i-1]

Unlike OBV (which adds the whole bar's volume on up closes), PVT weights
volume by the percentage price change, so a 0.1% drift adds far less than
a 5% thrust. No lookahead: every value on bar i uses bars through i only.
"""

import pandas as pd

from strategies import base as B

PVT_MA = 20
REGIME_SMA = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    v = df["v"]
    pct = c.pct_change().fillna(0.0)
    df["pvt"] = (v * pct).cumsum()
    df["pvt_ma"] = B.sma(df["pvt"], PVT_MA)
    df["regime_sma"] = B.sma(c, REGIME_SMA)
    return df
