"""Bollinger-on-RSI signals (exhaustion mean reversion).

long_entry  = RSI crosses back above its lower band (was stretched below)
short_entry = RSI crosses back below its upper band (was stretched above)
long_exit   = RSI crosses above its band midline
short_exit  = RSI crosses below its band midline
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = df["rsi"]
    upper, mid, lower = df["rsi_bb_upper"], df["rsi_bb_mid"], df["rsi_bb_lower"]
    df["long_entry"] = B.crossed_above(rsi, lower)
    df["short_entry"] = B.crossed_below(rsi, upper)
    df["long_exit"] = B.crossed_above(rsi, mid)
    df["short_exit"] = B.crossed_below(rsi, mid)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
