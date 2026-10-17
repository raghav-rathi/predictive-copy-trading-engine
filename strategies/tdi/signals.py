"""TDI signals (Malone's E.A.S.Y. rules, both directions).

long_entry  = green crosses above red while yellow > 50 (bullish regime)
short_entry = green crosses below red while yellow < 50 (bearish regime)
long_exit   = green crosses back below red OR green > 68 (overbought)
short_exit  = green crosses back above red OR green < 32 (oversold)
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    g, r, y = df["tdi_green"], df["tdi_red"], df["tdi_yellow"]
    long_x = B.crossed_above(g, r) & (y > 50)
    short_x = B.crossed_below(g, r) & (y < 50)
    df["long_entry"] = long_x.fillna(False)
    df["short_entry"] = short_x.fillna(False)
    df["long_exit"] = (B.crossed_below(g, r) | (g > 68)).fillna(False)
    df["short_exit"] = (B.crossed_above(g, r) | (g < 32)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
