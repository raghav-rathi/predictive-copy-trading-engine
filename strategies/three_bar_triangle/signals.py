"""Raschke 3-bar triangle signals.

Long entry:  within 5 bars after a contraction bar, close breaks
             above the triangle high AND volume > 1.25x SMA(v, 20).
Short entry: mirror — close below the triangle low with volume
             expansion.
Long exit:   close back below the triangle low (failed breakout)
             OR an opposite triangle signal.
Short exit:  close back above the triangle high OR an opposite
             triangle signal.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vol_ok = (df["v"] > 1.25 * df["vol_ma20"]).fillna(False)
    break_up = (df["c"] > df["tri_high"]).fillna(False)
    break_dn = (df["c"] < df["tri_low"]).fillna(False)
    df["long_entry"] = (break_up & vol_ok).astype(bool)
    df["short_entry"] = (break_dn & vol_ok).astype(bool)
    df["long_exit"] = (break_dn | df["short_entry"]).astype(bool)
    df["short_exit"] = (break_up | df["long_entry"]).astype(bool)
    return df
