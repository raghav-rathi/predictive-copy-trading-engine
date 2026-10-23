"""Engulfing reversal traded WITH the trend.

Canon (see README.md sources): act on the CLOSED engulfing candle,
never intrabar; engulfings are location- and trend-dependent, so the
signal demands trend alignment via EMA(20):

    long_entry  = bullish_eng & (c > ema20)   # dip-buy the engulfing in an uptrend
    short_entry = bearish_eng & (c < ema20)   # rally-sell the engulfing in a downtrend
    long_exit   = bearish_eng                  # opposite pattern kills the trade
    short_exit  = bullish_eng

The trend filter reads the engulfing bar's own close and EMA(20) at
that bar's close — both known when the bar closes, so no lookahead.
The harness executes entries/exits at the next bar's open.

Signal columns are boolean, no NaN, no lookahead. bullish_eng and
bearish_eng are mutually exclusive (a bar cannot be both green and
red), so entry and exit never fire on the same bar for the same side.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    above = (df["c"] > df["ema20"]).fillna(False)
    below = (df["c"] < df["ema20"]).fillna(False)
    bull = df["bullish_eng"].fillna(False).astype(bool)
    bear = df["bearish_eng"].fillna(False).astype(bool)
    df["long_entry"] = (bull & above).astype(bool)
    df["short_entry"] = (bear & below).astype(bool)
    df["long_exit"] = bear.astype(bool)
    df["short_exit"] = bull.astype(bool)
    return df
