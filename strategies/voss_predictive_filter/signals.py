"""Voss Predictive Filter signals (Ehlers, TASC Aug 2019 Traders' Tip).

Long entry: Voss crosses above the band-pass line, gated by
ADX(14) < 25 (stay out when the trend is strong — the cycle signal
fails once a strong trend emerges).
Short entry: Voss crosses below the band-pass line, same ADX gate.
Long exit: Voss crosses below the band-pass line.
Short exit: Voss crosses above the band-pass line.

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

ADX_GATE = 25.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    weak_trend = (df["adx"] < ADX_GATE).fillna(False)
    cross_up = crossed_above(df["voss"], df["bandpass"]).fillna(False)
    cross_down = crossed_below(df["voss"], df["bandpass"]).fillna(False)
    df["long_entry"] = (cross_up & weak_trend).astype(bool)
    df["short_entry"] = (cross_down & weak_trend).astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
