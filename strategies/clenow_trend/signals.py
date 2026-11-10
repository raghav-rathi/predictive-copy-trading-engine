"""Clenow trend-following signals.

Long entry: the close breaks above the highest high of the previous
1200 bars (the prior 50-day high) while the trend filter is bullish
(EMA1200 > EMA2400). Short entry: the close breaks below the lowest
low of the previous 1200 bars while bearish.

Exits: a long exits on the opposite breakout — a close below the
prior 1200-bar low while bearish — and a short exits on a close above
the prior 1200-bar high while bullish. The 3x ATR trailing stop in
the risk layer does most of the exiting in practice; the signal exit
is the book's breakout-reversal exit.

DEVIATION (documented in CALIBRATION.md): the brief's literal rule —
close == the rolling 1200-bar high *including the current bar* — can
essentially never fire, because close <= high on every bar, so it
requires the current bar to both set the 1200-bar high and close
exactly on it. It fired 0 times in 17,323 window bars across the
three coins. The implemented rule compares the close against the
prior 1200 bars' extreme (the standard breakout definition, same
series and window), which is the closest faithful version.

All inputs are computed from data through bar i's close, so signals
on bar i use no future data.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bullish = df["bullish"].fillna(False).astype(bool)
    bearish = df["bearish"].fillna(False).astype(bool)
    # Prior-bar Donchian extremes: the rolling max/min through bar i-1,
    # so a close on bar i that breaks them is a genuine new extreme.
    # NaN on the first 1200 bars -> no entries before the window fills.
    prior_high = df["donchian_high_1200"].shift(1)
    prior_low = df["donchian_low_1200"].shift(1)
    new_high = (df["c"] > prior_high).fillna(False)
    new_low = (df["c"] < prior_low).fillna(False)
    df["long_entry"] = (new_high & bullish).fillna(False).astype(bool)
    df["short_entry"] = (new_low & bearish).fillna(False).astype(bool)
    df["long_exit"] = (new_low & bearish).fillna(False).astype(bool)
    df["short_exit"] = (new_high & bullish).fillna(False).astype(bool)
    return df
