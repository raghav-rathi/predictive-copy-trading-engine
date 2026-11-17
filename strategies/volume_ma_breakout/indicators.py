"""Volume-confirmed breakout indicators.

Classic volume-confirmed breakout: a new 20-bar extreme is only
trusted when volume confirms it.

Long breakout:
    close makes a new 20-bar high (high >= trailing 20-bar high,
    current bar included) AND volume > 1.5x the trailing 20-bar
    mean volume (previous 20 bars, shifted by 1, so the current
    bar's own spike does not dilute the mean).

Short breakout: mirror image on a new 20-bar low.

Exits use the trailing 10-bar range EXCLUDING the current bar
(the current bar's own low can never be above its close, so an
inclusive 10-bar low could never trigger a long exit):
    long exit:  close below the trailing 10-bar low (prior 10 bars)
    short exit: close above the trailing 10-bar high (prior 10 bars)

Columns:

    high_20, low_20     -- trailing 20-bar high/low (incl. current)
    vol_mean_20         -- mean volume of the previous 20 bars
    vol_ratio           -- volume / vol_mean_20
    long_breakout       -- bool, as defined above
    short_breakout      -- bool, as defined above
    low_10_prev         -- trailing 10-bar low, previous 10 bars
    high_10_prev        -- trailing 10-bar high, previous 10 bars
    atr                 -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

BREAKOUT_N = 20
VOL_MULT = 1.5
EXIT_N = 10

INDICATOR_COLS = ["high_20", "low_20", "vol_mean_20", "vol_ratio",
                  "long_breakout", "short_breakout",
                  "low_10_prev", "high_10_prev", "atr"]


def add_indicators(df: pd.DataFrame, n: int = BREAKOUT_N,
                   vol_mult: float = VOL_MULT,
                   exit_n: int = EXIT_N) -> pd.DataFrame:
    df = df.copy()
    high20 = df["h"].rolling(n, min_periods=n).max()
    low20 = df["l"].rolling(n, min_periods=n).min()
    vol_mean = df["v"].rolling(n, min_periods=n).mean().shift(1)
    vol_ratio = df["v"] / vol_mean
    is_new_high = (df["h"] >= high20).fillna(False)
    is_new_low = (df["l"] <= low20).fillna(False)
    vol_spike = (vol_ratio > vol_mult).fillna(False)
    long_breakout = is_new_high & vol_spike
    short_breakout = is_new_low & vol_spike
    low_10_prev = df["l"].rolling(exit_n, min_periods=exit_n).min().shift(1)
    high_10_prev = df["h"].rolling(exit_n, min_periods=exit_n).max().shift(1)
    df["high_20"] = high20
    df["low_20"] = low20
    df["vol_mean_20"] = vol_mean
    df["vol_ratio"] = vol_ratio
    df["long_breakout"] = long_breakout.astype(bool)
    df["short_breakout"] = short_breakout.astype(bool)
    df["low_10_prev"] = low_10_prev
    df["high_10_prev"] = high_10_prev
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
