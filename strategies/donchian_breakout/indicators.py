"""Donchian Channel Breakout indicators.

Donchian(20): the upper channel is the highest high of the PRIOR
20 bars (bars i-20..i-1) and the lower channel is the lowest low of
the PRIOR 20 bars. The Turtle 10-bar exit uses the lowest low /
highest high of the PRIOR 10 bars. All windows are trailing and
shifted by one bar, so every value on bar i uses data through bar
i-1 only for the channel levels (the close on bar i is compared
against them in signals.py).

Columns:
    dc_upper / dc_lower -- Donchian channel (prior 20 bars)
    dc_mid -- (dc_upper + dc_lower) / 2
    exit_low / exit_high -- Turtle 10-bar exit levels (prior 10 bars)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every channel level on bar i uses bars i-20..i-1
(and i-10..i-1 for the exit levels) only.
"""

import pandas as pd

from strategies import base as B

CHAN_N = 20
EXIT_N = 10
ATR_N = 14


def add_indicators(df: pd.DataFrame, chan_n: int = CHAN_N,
                   exit_n: int = EXIT_N, atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]

    df["dc_upper"] = h.rolling(chan_n, min_periods=chan_n).max().shift(1)
    df["dc_lower"] = l.rolling(chan_n, min_periods=chan_n).min().shift(1)
    df["dc_mid"] = (df["dc_upper"] + df["dc_lower"]) / 2
    df["exit_low"] = l.rolling(exit_n, min_periods=exit_n).min().shift(1)
    df["exit_high"] = h.rolling(exit_n, min_periods=exit_n).max().shift(1)
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
