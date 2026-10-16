"""Schaff Trend Cycle signals.

STC is a 0-100 oscillator: crosses through the 25/75 bands mark momentum
turns from oversold/overbought extremes.

Long entry  : stc crosses UP through 25   (oversold turn)
Short entry : stc crosses DOWN through 75 (overbought turn)
Long exit   : stc crosses DOWN through 75 (opposing cross)
Short exit  : stc crosses UP through 25   (opposing cross)

All crosses use stc_s (STC formed at the current bar's close).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (df["stc_s"] > 25) & (df["stc_s"].shift(1) <= 25)
    df["short_entry"] = (df["stc_s"] < 75) & (df["stc_s"].shift(1) >= 75)
    df["long_exit"] = (df["stc_s"] < 75) & (df["stc_s"].shift(1) >= 75)
    df["short_exit"] = (df["stc_s"] > 25) & (df["stc_s"].shift(1) <= 25)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
