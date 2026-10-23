"""Breakout-retest (throwback) indicators: the polarity principle.

Old resistance becomes new support, old support becomes new
resistance. A level is the 20-bar rolling extreme of the range;
a breakout is a close that crosses it; the retest logic lives in
signals.py, which tracks each breakout's level over a 20-bar
window.

Columns:

    level_high   -- rolling(20).max() of h (resistance line)
    level_low    -- rolling(20).min() of l (support line)
    breakout_up  -- crossed_above(c, level_high.shift(1))
    breakout_dn  -- crossed_below(c, level_low.shift(1))
    atr          -- Wilder ATR(14) for the retest touch/loss bands

No lookahead: level_high[j] uses h[j-19..j] only (min_periods=20),
and the breakout crosses are taken against the *shifted* level,
so the signal on bar j uses only data available at bar j's close.
"""

import pandas as pd

from strategies.base import atr, crossed_above, crossed_below

RANGE_N = 20    # range lookback (fixed a priori)
ATR_N = 14      # ATR window (fixed a priori)


def add_indicators(df: pd.DataFrame, n: int = RANGE_N) -> pd.DataFrame:
    df = df.copy()
    level_high = df["h"].rolling(n, min_periods=n).max().rename("level_high")
    level_low = df["l"].rolling(n, min_periods=n).min().rename("level_low")
    df["level_high"] = level_high
    df["level_low"] = level_low
    df["breakout_up"] = crossed_above(df["c"], level_high.shift(1)).fillna(False).astype(bool)
    df["breakout_dn"] = crossed_below(df["c"], level_low.shift(1)).fillna(False).astype(bool)
    df["atr"] = atr(df["h"], df["l"], df["c"], ATR_N)
    return df
