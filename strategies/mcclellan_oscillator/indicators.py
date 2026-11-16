"""McClellan Oscillator (single-asset candle-count proxy).

The classic McClellan Oscillator is a breadth oscillator built from
exchange advance/decline data: RANA = 1000 * (advances - declines) /
(advances + declines), oscillator = EMA19(RANA) - EMA39(RANA), and
the summation index is the cumulative sum of the oscillator.

We have no exchange breadth feed on 1h crypto candles, so this is a
single-asset proxy: a bar counts as an "advance" when close > open
and a "decline" when close < open (doji bars, close == open, are
neutral and count in neither leg), tallied over a rolling 24-bar
window. That is a candle-count proxy for breadth, NOT true
advance/decline data — see README.md.

    rana          -- 1000 * (up - down) / max(up + down, 1), rolling 24
    mc_osc        -- EMA19(rana) - EMA39(rana)
    mc_summation  -- cumulative sum of mc_osc (NaN treated as 0 pre-spin-up)
    atr           -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar j uses bars through j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW = 24  # shipped default: breadth tally window (bars)
EMA_FAST = 19  # shipped default
EMA_SLOW = 39  # shipped default


def rana(o: pd.Series, c: pd.Series, window: int = WINDOW) -> pd.Series:
    """Net-advance ratio over a rolling window, scaled to [-1000, 1000]."""
    up = (c > o).astype(float)
    down = (c < o).astype(float)
    up_n = up.rolling(window, min_periods=window).sum()
    down_n = down.rolling(window, min_periods=window).sum()
    denom = (up_n + down_n).clip(lower=1.0)
    return 1000.0 * (up_n - down_n) / denom


def add_indicators(df: pd.DataFrame, window: int = WINDOW,
                   fast: int = EMA_FAST, slow: int = EMA_SLOW) -> pd.DataFrame:
    df = df.copy()
    df["rana"] = rana(df["o"], df["c"], window)
    df["mc_osc"] = B.ema(df["rana"], fast) - B.ema(df["rana"], slow)
    # Summation index: cumulate the oscillator; pre-spin-up NaNs count as 0
    # so the index is defined from bar 0 and only moves once osc exists.
    df["mc_summation"] = df["mc_osc"].fillna(0.0).cumsum()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
