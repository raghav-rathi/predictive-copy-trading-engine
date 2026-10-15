"""Wyckoff spring/upthrust indicators (Richard Wyckoff).

A spring: price pokes BELOW the 50-bar range support and closes back
INSIDE the range — the classic shakeout of weak hands before markup.
An upthrust: price pokes ABOVE the 50-bar range resistance and closes
back INSIDE — distribution before markdown.

  spring   = low[i]  < range_low[i-1]  and close[i] > range_low[i-1]
  upthrust = high[i] > range_high[i-1] and close[i] < range_high[i-1]

Range edges are taken from the PRIOR bar (shifted) so the poke is
measured against a level known before bar i — no lookahead. A volume
filter (volume > 20-bar SMA) requires the shakeout to happen on
participation, per Wyckoff's effort-vs-result law.
"""

import pandas as pd

from strategies import base as B

RANGE_N = 50
VOL_SMA = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    prev_high = h.rolling(RANGE_N, min_periods=RANGE_N).max().shift(1)
    prev_low = l.rolling(RANGE_N, min_periods=RANGE_N).min().shift(1)
    df["range_high"] = prev_high
    df["range_low"] = prev_low
    df["spring"] = ((l < prev_low) & (c > prev_low)).fillna(False)
    df["upthrust"] = ((h > prev_high) & (c < prev_high)).fillna(False)
    df["vol_ok"] = (v > B.sma(v, VOL_SMA)).fillna(False)
    return df
