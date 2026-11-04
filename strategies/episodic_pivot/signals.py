"""Episodic Pivot signals (long-only)."""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ep = (
        (df["gap_pct"] >= 0.02)
        & (df["rel_vol"] >= 3.0)
        & (df["quiet_base"].shift(1).fillna(False))
        & (df["c"] > df["base_high"])
    )
    df["long_entry"] = ep.fillna(False).astype(bool)
    df["short_entry"] = False
    df["long_exit"] = (df["c"] < df["sma20"]).astype(bool)
    df["short_exit"] = False
    return df
