"""StochRSI signals: %K/%D crosses in the oversold/overbought zones.

long_entry  = %K crosses above %D while BOTH are below OS (20)
short_entry = %K crosses below %D while BOTH are above OB (80)
long_exit   = %K crosses below %D (opposite momentum turn, any zone)
short_exit  = %K crosses above %D

The zone gate on entries is the classic Chande/Kroll usage: only take the
cross when the oscillator is at an extreme. Exits use the raw cross so a
winning trade is not held through the full momentum reversal. Execution is
next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B

OS = 20.0
OB = 80.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stochrsi_k"]
    d = df["stochrsi_d"]
    cross_up = B.crossed_above(k, d)
    cross_dn = B.crossed_below(k, d)
    df["long_entry"] = cross_up & (k < OS) & (d < OS)
    df["short_entry"] = cross_dn & (k > OB) & (d > OB)
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
