"""Momentum Pinball signals (fade the LBR/RSI extreme).

long_entry  = pinball crosses back above the BUY_DAY line from below
              (i.e. pinball < 30 then turns up: the "buy day" flip)
short_entry = pinball crosses back below the SELL_DAY line from above
              (the "sell day" flip)
long_exit   = pinball crosses back above SELL_DAY (momentum exhausted)
short_exit  = pinball crosses back below BUY_DAY
Crypto adaptation: on daily equities the book enters above the first
hour's high the next day; on 1h crypto bars the flip itself is the
entry signal, executed next-bar-open per the harness contract.
"""

import pandas as pd

from strategies.momentum_pinball import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pb, pb_prev = df["pinball"], df["pinball_prev"]
    # "buy day": was oversold, now hooking up
    buy_flip = (pb_prev <= I.BUY_DAY) & (pb > pb_prev)
    sell_flip = (pb_prev >= I.SELL_DAY) & (pb < pb_prev)
    # exhaustion: momentum has rotated fully to the other extreme
    df["long_entry"] = buy_flip.fillna(False)
    df["short_entry"] = sell_flip.fillna(False)
    df["long_exit"] = (pb >= I.SELL_DAY).fillna(False)
    df["short_exit"] = (pb <= I.BUY_DAY).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
