"""Mass Index signals.

Long entry:  reversal bulge completes (MI > 27 then < 26.5) with close < SMA(20).
Short entry: bulge completes with close > SMA(20).
Exits: opposite bulge completion; the 3xATR trailing stop lives in risk.py
(trail_atr_mult) and is enforced by the harness.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["bulge_long"]
    df["short_entry"] = df["bulge_short"]
    df["long_exit"] = df["bulge_short"]
    df["short_exit"] = df["bulge_long"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
