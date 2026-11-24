"""Livermore trend-system indicators (Jesse Livermore).

Higher highs / higher lows define an uptrend; lower highs /
lower lows a downtrend. All levels are prior-bar windows, so
a close can actually break them:

    brk_high -- highest high of the prior 20 bars (excl. current)
    brk_low  -- lowest low of the prior 20 bars (excl. current)
    low10_a  -- 10-bar low ending 10 bars ago (bars i-19 .. i-10)
    low10_b  -- 10-bar low ending 20 bars ago (bars i-29 .. i-20)
    high10_a -- 10-bar high ending 10 bars ago
    high10_b -- 10-bar high ending 20 bars ago
    higher_lows -- low10_a > low10_b (the swing lows are rising)
    lower_highs -- high10_a < high10_b (the swing highs are falling)
    exit_low  -- lowest low of the prior 10 bars (exit trigger)
    exit_high -- highest high of the prior 10 bars (exit trigger)

Columns: brk_high, brk_low, low10_a, low10_b, high10_a,
high10_b, higher_lows, lower_highs, exit_low, exit_high.

No lookahead: every value on bar j uses data through bar j's
close only (all windows are shifted by at least one bar).
"""

import pandas as pd

BREAKOUT_LOOKBACK = 20  # shipped default
SWING_N = 10            # swing-low/high window for the higher-lows test


def add_indicators(
    df: pd.DataFrame,
    breakout_lookback: int = BREAKOUT_LOOKBACK,
    swing_n: int = SWING_N,
) -> pd.DataFrame:
    df = df.copy()
    n = breakout_lookback
    df["brk_high"] = df["h"].rolling(n, min_periods=n).max().shift(1)
    df["brk_low"] = df["l"].rolling(n, min_periods=n).min().shift(1)
    df["low10_a"] = df["l"].rolling(swing_n, min_periods=swing_n).min().shift(swing_n)
    df["low10_b"] = df["l"].rolling(swing_n, min_periods=swing_n).min().shift(2 * swing_n)
    df["high10_a"] = df["h"].rolling(swing_n, min_periods=swing_n).max().shift(swing_n)
    df["high10_b"] = df["h"].rolling(swing_n, min_periods=swing_n).max().shift(2 * swing_n)
    df["higher_lows"] = df["low10_a"] > df["low10_b"]
    df["lower_highs"] = df["high10_a"] < df["high10_b"]
    df["exit_low"] = df["l"].rolling(swing_n, min_periods=swing_n).min().shift(1)
    df["exit_high"] = df["h"].rolling(swing_n, min_periods=swing_n).max().shift(1)
    return df
