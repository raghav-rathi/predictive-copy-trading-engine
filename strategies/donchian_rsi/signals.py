"""Donchian + RSI signals.

Long entry:  close breaks above the prior 20-bar high AND RSI(14) > 55.
Short entry: close breaks below the prior 20-bar low AND RSI(14) < 45.
Long exit:   close breaks below the prior 20-bar low (the opposite
             Donchian breakout).
Short exit:  close breaks above the prior 20-bar high.

The RSI confirmation is a level check on the breakout bar (not a
cross): the breakout must already carry momentum. The exits are pure
Donchian — no RSI condition — so a position is closed as soon as the
opposite extreme breaks, even if RSI still agrees with the trade.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_break = (df["c"] > df["don_high20"]).fillna(False)
    short_break = (df["c"] < df["don_low20"]).fillna(False)
    rsi_long = (df["rsi"] > 55).fillna(False)
    rsi_short = (df["rsi"] < 45).fillna(False)
    df["long_entry"] = (long_break & rsi_long).astype(bool)
    df["short_entry"] = (short_break & rsi_short).astype(bool)
    df["long_exit"] = short_break.astype(bool)
    df["short_exit"] = long_break.astype(bool)
    return df
