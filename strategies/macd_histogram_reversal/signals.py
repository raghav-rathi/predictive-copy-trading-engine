"""Elder MACD-histogram slope-flip signals.

A histogram trough flip: hist[i] > hist[i-1] while
hist[i-1] <= hist[i-2] — the histogram's decline has just
reversed into an uptick. A peak flip is the mirror. Elder's
filter is the histogram's own sign: a trough flip only counts
as a buy while the histogram is still below zero (momentum is
turning from bearish territory, not chasing an already-positive
run), and a peak flip only counts as a sell while it is still
above zero.

    long_entry  -- trough flip with hist < 0
    short_entry -- peak flip with hist > 0
    long_exit   -- peak flip with hist > 0, or hist crosses
                   below zero (the turn gave everything back)
    short_exit  -- trough flip with hist < 0, or hist crosses
                   above zero

So a flip both exits one side and may enter the other on the
same bar — the harness exits first, then enters, which is the
intended reversal behaviour. All conditions read bar-i closes
(the flip needs hist[i-2..i] only); the harness executes at
bar i+1's open. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hist = df["macd_hist"]
    prev = hist.shift(1)
    prev2 = hist.shift(2)

    trough_flip = (hist > prev) & (prev <= prev2)
    peak_flip = (hist < prev) & (prev >= prev2)

    df["long_entry"] = (trough_flip & (hist < 0)).fillna(False).astype(bool)
    df["short_entry"] = (peak_flip & (hist > 0)).fillna(False).astype(bool)
    df["long_exit"] = (
        (peak_flip & (hist > 0)) | crossed_below(hist, 0)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (trough_flip & (hist < 0)) | crossed_above(hist, 0)
    ).fillna(False).astype(bool)
    return df
