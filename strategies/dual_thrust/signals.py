"""Dual Thrust signals: session-breakout entries with reversing exits.

long_entry  = close crosses above BuyLine
            (prev close <= prev BuyLine and close > BuyLine)
short_entry = close crosses below SellLine
            (prev close >= prev SellLine and close < SellLine)
Reversing system: a long entry also exits an open short and vice versa,
so long_exit == short_entry and short_exit == long_entry. Execution is
next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["c"], df["buy_line"])
    df["short_entry"] = B.crossed_below(df["c"], df["sell_line"])
    # reversing exits: the opposite-side entry closes the position
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
