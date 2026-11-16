"""Wavelet-trend signals.

    long_entry  = approximation slope (5-bar) turns positive and
                  close above the approximation
    short_entry = approximation slope turns negative and close below
                  the approximation

Exits: the approximation slope flips against the position, or close
crosses the approximation the other way.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    slope = df["wav_slope"]
    prev = slope.shift(1)
    slope_up = (slope > 0) & (prev <= 0)
    slope_dn = (slope < 0) & (prev >= 0)
    close = df["c"]
    approx = df["wav_approx"]
    df["long_entry"] = (slope_up & (close > approx)).fillna(False).astype(bool)
    df["short_entry"] = (slope_dn & (close < approx)).fillna(False).astype(bool)
    df["long_exit"] = (slope_dn | crossed_below(close, approx)).fillna(False).astype(bool)
    df["short_exit"] = (slope_up | crossed_above(close, approx)).fillna(False).astype(bool)
    return df
