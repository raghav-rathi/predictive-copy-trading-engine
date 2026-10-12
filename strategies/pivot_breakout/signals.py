"""Pivot breakout signals: prior-day R1/S1 break-and-close entries.

long_entry  = 1h close crosses above prior day's R1
short_entry = 1h close crosses below prior day's S1
long_exit   = close touches the opposite side (close <= S1)
short_exit  = close touches the opposite side (close >= R1)

The R1 > prior close sanity check from the task spec is inherent to
24/7 crypto: R1 >= PP always holds (R1 - PP = (H - L)/3 >= 0), and with
no session gaps the break-and-close rule fires only on real intraday
expansion past the level. The ATR(14)x2 hard stop lives in risk.py and
catches failed-breakout reversals. Execution is next-bar-open per the
harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["c"], df["r1"])
    df["short_entry"] = B.crossed_below(df["c"], df["s1"])
    df["long_exit"] = df["c"] <= df["s1"]
    df["short_exit"] = df["c"] >= df["r1"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
