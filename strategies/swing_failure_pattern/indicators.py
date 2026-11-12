"""Swing Failure Pattern indicators (Larry Williams, false breakout).

A swing high is the highest high of the prior 20 bars (excluding the
current bar); a swing low is the lowest low of the prior 20 bars.
A new 20-bar high that cannot hold — price closes back below the swing
high — is a bearish swing failure (a failed breakout / liquidity
sweep); the mirror at a swing low is a bullish failure.

Columns:

    swing_high -- highest high of the prior 20 bars (excl. current)
    swing_low  -- lowest low of the prior 20 bars (excl. current)
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: the swing levels on bar i use only bars i-20..i-1, and
the failure is detected on bar i's own close.
"""

import pandas as pd

from strategies import base as B

LOOKBACK = 20

INDICATOR_COLS = ["swing_high", "swing_low", "atr"]


def add_indicators(df: pd.DataFrame, n: int = LOOKBACK) -> pd.DataFrame:
    df = df.copy()
    df["swing_high"] = df["h"].shift(1).rolling(n, min_periods=n).max()
    df["swing_low"] = df["l"].shift(1).rolling(n, min_periods=n).min()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
