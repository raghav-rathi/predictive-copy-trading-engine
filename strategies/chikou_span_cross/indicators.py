"""Ichimoku Chikou-span indicators.

The Chikou span is today's closing price projected back 26 periods:
at bar i it is compared against the price as of 26 bars ago, i.e.
``chikou_ref = close.shift(26)``. A cross of the current close above
/ below that reference is exactly the Chikou span crossing the price
as of 26 bars ago (Wikipedia, Ichimoku Kinko Hyo: "If the Chikou
Span ... crosses the price in the bottom-up direction, that is a buy
signal. If the green line crosses the price from the top-down, that
is a sell signal").

NOTE: the shared ``strategies.base.ichimoku`` helper computes chikou
as ``close.shift(-26)`` (the close plotted 26 bars FORWARD), which
uses future data and is NOT used here. This module only ever looks
backwards, so there is no lookahead.
"""

import pandas as pd

CHIKOU_PERIOD = 26

INDICATOR_COLS = [
    "chikou_ref",
    "chikou_diff",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["chikou_ref"] = df["c"].shift(CHIKOU_PERIOD)
    df["chikou_diff"] = df["c"] - df["chikou_ref"]
    return df
