"""Price channel breakout indicators (Richard Donchian, 1960s).

Channel high = highest high of the prior 30 bars.
Channel low  = lowest low of the prior 30 bars.
Midline      = (channel high + channel low) / 2.

The channel bands use the prior 30 bars only (the current bar is
excluded), so a close above the channel high is a genuine new 30-bar
high. The midline is the average of the two bands, not the average of
every price in the window.

Columns:

    channel_high  -- rolling 30-bar max of high, excluding the current bar
    channel_low   -- rolling 30-bar min of low, excluding the current bar
    channel_mid   -- (channel_high + channel_low) / 2
    atr           -- Wilder ATR(14) for the risk layer

No lookahead: the bands use only bars before bar i, so everything on
bar i is known at bar i's close.
"""

import pandas as pd

from strategies import base as B

CHANNEL_N = 30

INDICATOR_COLS = ["channel_high", "channel_low", "channel_mid", "atr"]


def add_indicators(df: pd.DataFrame, n: int = CHANNEL_N) -> pd.DataFrame:
    df = df.copy()
    df["channel_high"] = df["h"].shift(1).rolling(n, min_periods=n).max()
    df["channel_low"] = df["l"].shift(1).rolling(n, min_periods=n).min()
    df["channel_mid"] = (df["channel_high"] + df["channel_low"]) / 2.0
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
