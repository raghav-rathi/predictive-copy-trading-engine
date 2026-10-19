"""TEMA trend signals (Patrick Mulloy).

Long when TEMA20 crosses above TEMA50 with price above the SMA200
regime filter; short when TEMA20 crosses below TEMA50 with price below
SMA200. Exit on the TEMA cross flipping against the position (the
harness's 3xATR chandelier also trails winners).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast, slow, regime = df["tema_fast"], df["tema_slow"], df["sma_regime"]
    c = df["c"]
    prev_fast, prev_slow = fast.shift(1), slow.shift(1)
    cross_up = ((prev_fast <= prev_slow) & (fast > slow)).fillna(False)
    cross_dn = ((prev_fast >= prev_slow) & (fast < slow)).fillna(False)
    df["long_entry"] = (cross_up & (c > regime)).fillna(False)
    df["short_entry"] = (cross_dn & (c < regime)).fillna(False)
    df["long_exit"] = cross_dn.fillna(False)
    df["short_exit"] = cross_up.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
