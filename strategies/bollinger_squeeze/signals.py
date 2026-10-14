"""Bollinger squeeze signals.

Squeeze release: squeezed on the prior bar, not squeezed now.
  Long  on release with close > Keltner mid and momentum > 0
  Short on release with close < Keltner mid and momentum < 0
Exit on opposite release, or close crossing back through the Keltner mid.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    release = df["squeeze_prev"].fillna(False) & (~df["squeeze"].fillna(True))
    df["long_entry"] = release & (df["c"] > df["kc_mid"]) & (df["mom"] > 0)
    df["short_entry"] = release & (df["c"] < df["kc_mid"]) & (df["mom"] < 0)
    df["long_exit"] = release & (df["c"] < df["kc_mid"])
    df["short_exit"] = release & (df["c"] > df["kc_mid"])
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
