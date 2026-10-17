"""Liquidity-sweep reversal signals.

short_entry = sweep of buy-side liquidity (wick above the pool high,
              close back inside): fade the stop hunt
long_entry  = sweep of sell-side liquidity (wick below the pool low,
              close back inside)
long_exit   = opposite sweep OR the pool high breaks on a CLOSE
              (invalidation: it was a breakout, not a sweep)
short_exit  = opposite sweep OR the pool low breaks on a CLOSE
Execution next-bar-open per the harness contract; the harness hard stop
sits beyond the sweep extreme.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    su, sd = df["sweep_up"], df["sweep_dn"]
    ph, pl = df["pool_high"], df["pool_low"]
    df["long_entry"] = sd.fillna(False)
    df["short_entry"] = su.fillna(False)
    # breakout-close invalidation of the faded level
    long_invalid = (df["c"] > ph).fillna(False)
    short_invalid = (df["c"] < pl).fillna(False)
    df["long_exit"] = (su | long_invalid).fillna(False)
    df["short_exit"] = (sd | short_invalid).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
