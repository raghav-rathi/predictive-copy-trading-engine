"""Donchian channel breakout + RSI filter indicators.

Richard Donchian's channel: the highest high and lowest low of
the last n periods (n = 20 by default; the Turtle exit channel
is n = 10). RSI(14) via base.rsi filters out overextended
breakouts — longs only while RSI < 70, shorts only while
RSI > 30.

Columns:
    donchian_high_20, donchian_low_20 -- 20-bar entry channel
    donchian_high_10, donchian_low_10 -- 10-bar Turtle exit channel
    rsi                                -- Wilder RSI(14)
    atr14                              -- ATR(14), diagnostic

No lookahead: rolling extremes and Wilder RSI are causal; the
signals shift the channels by one bar so a breakout is judged
against the prior bars' channel, never the current bar's own
high/low.
"""

import pandas as pd

from strategies import base as B

ENTRY_N = 20
EXIT_N = 10
RSI_N = 14


def add_indicators(
    df: pd.DataFrame,
    entry_n: int = ENTRY_N,
    exit_n: int = EXIT_N,
    rsi_n: int = RSI_N,
) -> pd.DataFrame:
    df = df.copy()
    d_entry = B.donchian(df["h"], df["l"], entry_n)
    df[f"donchian_high_{entry_n}"] = d_entry[f"donchian_high_{entry_n}"]
    df[f"donchian_low_{entry_n}"] = d_entry[f"donchian_low_{entry_n}"]
    d_exit = B.donchian(df["h"], df["l"], exit_n)
    df[f"donchian_high_{exit_n}"] = d_exit[f"donchian_high_{exit_n}"]
    df[f"donchian_low_{exit_n}"] = d_exit[f"donchian_low_{exit_n}"]
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
