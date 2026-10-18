"""Tom DeMark TD Combo signals.

Entries: long on a completed buy countdown (13), short on a completed
sell countdown (13).  Exits: the price flip — the setup's flip condition
reversing (longs exit when close > close[4], shorts when close <
close[4]) — plus the 24-bar max hold from risk.py (time stop) and the
1xATR hard stop (standing in for the 13-count low/high).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["buy_countdown_complete"].fillna(False)
    df["short_entry"] = df["sell_countdown_complete"].fillna(False)
    c4 = df["c"].shift(4)
    df["long_exit"] = (df["c"] > c4).fillna(False)
    df["short_exit"] = (df["c"] < c4).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
