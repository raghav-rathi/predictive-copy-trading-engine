"""FFT dominant-cycle signals.

    long_entry  = fft_slope turns up (<= 0 -> > 0) and close > SMA(50)
    short_entry = fft_slope turns down (>= 0 -> < 0) and close < SMA(50)

Exits: the slope flips sign against the position, or price crosses
SMA(50) against the position.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    slope = df["fft_slope"]
    prev = slope.shift(1)
    slope_up = (slope > 0) & (prev <= 0)
    slope_dn = (slope < 0) & (prev >= 0)
    close = df["c"]
    sma = df["sma50"]
    above = close > sma
    below = close < sma
    df["long_entry"] = (slope_up & above).fillna(False).astype(bool)
    df["short_entry"] = (slope_dn & below).fillna(False).astype(bool)
    df["long_exit"] = (slope_dn | crossed_below(close, sma)).fillna(False).astype(bool)
    df["short_exit"] = (slope_up | crossed_above(close, sma)).fillna(False).astype(bool)
    return df
