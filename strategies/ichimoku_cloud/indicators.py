"""Ichimoku Cloud (9/26/52) indicators.

NOTE: B.ichimoku() returns a 'chikou' column computed as c.shift(-26),
which contains FUTURE closes. It is NOT stored here and is never used in
signals. The Chikou check is computed directly in signals.py as
c > c.shift(26) (long) / c < c.shift(26) (short), which uses only past data.
Senkou spans from B.ichimoku() are already shifted +26, so the cloud value
at bar i is the one computed 26 bars ago — correct to use."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["tenkan", "kijun", "senkou_a", "senkou_b"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ich = B.ichimoku(df["h"], df["l"], df["c"])
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    df["senkou_a"] = ich["senkou_a"]
    df["senkou_b"] = ich["senkou_b"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
