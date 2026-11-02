"""Keltner channel breakout indicators (Chester Keltner).

Channel = EMA(20) +/- 2.0 x ATR(10). The 2.0 multiplier is wider
than the common 1.5 trend-following setting, so a close outside
the channel is a genuine volatility expansion, not a routine
excursion.

Columns:
    kc_mid, kc_upper, kc_lower, atr
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"], ema_n=20, atr_n=10, k=2.0)
    for col in kc.columns:
        df[col] = kc[col]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
