"""VWMA cross signals.

long_entry  = VWMA(20) crosses above VWMA(50) with volume above its
              20-bar average (conviction)
short_entry = VWMA(20) crosses below VWMA(50) with volume confirmation
long_exit   = VWMA(20) crosses back below VWMA(50)
short_exit  = VWMA(20) crosses back above VWMA(50)
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    f, s, vok = df["vwma_fast"], df["vwma_slow"], df["vol_ok"]
    long_x = B.crossed_above(f, s) & vok
    short_x = B.crossed_below(f, s) & vok
    df["long_entry"] = long_x.fillna(False)
    df["short_entry"] = short_x.fillna(False)
    df["long_exit"] = B.crossed_below(f, s).fillna(False)
    df["short_exit"] = B.crossed_above(f, s).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
