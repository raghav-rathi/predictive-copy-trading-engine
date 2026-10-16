"""Chande & Kroll stop indicators.

From "The New Technical Trader" (Tushar Chande & Stanley Kroll):
  long-stop line  = rolling-max(q) of (highest-high(p) - x * ATR(10))
  short-stop line = rolling-min(q) of (lowest-low(p) + x * ATR(10))
with p=10, q=9, x=1.5. The q-period rolling max/min locks the stop lines
so they only tighten, never loosen, within the window.

Both lines are shifted by 1: a signal computed at bar i's close uses the
stop line formed through bar i-1 (no lookahead).
"""

import pandas as pd

from strategies import base as B

P = 10
Q = 9
X = 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]
    atr10 = B.atr(h, l, c, 10)
    highest_high_p = h.rolling(P, min_periods=P).max()
    lowest_low_p = l.rolling(P, min_periods=P).min()
    long_stop_line_raw = highest_high_p - X * atr10
    short_stop_line_raw = lowest_low_p + X * atr10
    long_stop_line = long_stop_line_raw.rolling(Q, min_periods=Q).max()
    short_stop_line = short_stop_line_raw.rolling(Q, min_periods=Q).min()
    df["long_stop"] = long_stop_line.shift(1)
    df["short_stop"] = short_stop_line.shift(1)
    df["sma21"] = B.sma(c, 21)
    df["atr"] = B.atr(h, l, c, 14)  # harness risk window
    return df
