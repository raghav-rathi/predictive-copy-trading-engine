"""Narrow-range breakout (NR7) indicators.

The setup bar is the bar whose range (h - l) is the smallest of the
last 7 bars including itself (Toby Crabel's NR7). The setup bar's high
and low, and the trend direction at the setup bar (SMA50 vs SMA200),
are carried forward for the 24 bars after the setup bar; a newer setup
bar replaces the old one. The setup columns are shifted by one bar so
a bar never trades off its own setup: nr_setup_high/low/dir on bar i
describe the most recent setup bar strictly before i.
"""

import numpy as np
import pandas as pd

from strategies.base import sma

NR_BARS = 7
SETUP_VALID_BARS = 24

INDICATOR_COLS = [
    "nr_range",
    "nr_is_nr7",
    "nr_setup_high",
    "nr_setup_low",
    "nr_setup_dir",
    "sma50",
    "sma200",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["nr_range"] = df["h"] - df["l"]
    df["nr_is_nr7"] = (
        df["nr_range"] == df["nr_range"].rolling(NR_BARS, min_periods=NR_BARS).min()
    ).fillna(False)
    sma50 = sma(df["c"], 50)
    sma200 = sma(df["c"], 200)
    df["sma50"] = sma50
    df["sma200"] = sma200
    is_setup = df["nr_is_nr7"]
    setup_high = df["h"].where(is_setup)
    setup_low = df["l"].where(is_setup)
    setup_dir = pd.Series(np.nan, index=df.index, dtype=float)
    setup_dir = setup_dir.mask(is_setup & (sma50 > sma200), 1.0)
    setup_dir = setup_dir.mask(is_setup & (sma50 < sma200), -1.0)
    # Forward-fill for the 24 bars after the setup bar: fill 23 bars
    # here, the shift below adds the 24th.
    df["nr_setup_high"] = setup_high.ffill(limit=SETUP_VALID_BARS - 1).shift(1)
    df["nr_setup_low"] = setup_low.ffill(limit=SETUP_VALID_BARS - 1).shift(1)
    df["nr_setup_dir"] = setup_dir.ffill(limit=SETUP_VALID_BARS - 1).shift(1)
    return df
