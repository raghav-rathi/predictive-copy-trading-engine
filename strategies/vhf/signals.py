"""VHF regime signals.

    long_entry  -- VHF crosses above 0.45 while close > SMA(28)
    short_entry -- VHF crosses above 0.45 while close < SMA(28)
    long_exit   -- VHF falls below 0.35 (trend regime ends)
    short_exit  -- VHF falls below 0.35 (trend regime ends)
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    regime_on = B.crossed_above(df["vhf"], 0.45).fillna(False)
    above = (df["c"] > df["sma28"]).fillna(False)
    below = (df["c"] < df["sma28"]).fillna(False)
    regime_off = (df["vhf"] < 0.35).fillna(False)
    df["long_entry"] = (regime_on & above).astype(bool)
    df["short_entry"] = (regime_on & below).astype(bool)
    df["long_exit"] = regime_off.astype(bool)
    df["short_exit"] = regime_off.astype(bool)
    return df
