"""Ehlers Relative Vigor Index indicators.

Plain-English idea: compare where the bar closed inside its own range
to what the range was. (close-open)/(high-low) is +1 when the bar
closes at the high and -1 at the low; smoothing that over 10 bars
gives the "vigor" of the move. Ehlers pairs it with a weighted signal
line (weights 1-2-2-1) that lags slightly less than a plain average.

Mechanics:
  raw    = (c - o) / (h - l), 0 when h == l (divide-by-zero guard)
  RVI    = SMA10(raw)
  signal = (RVI + 2*RVI[1] + 2*RVI[2] + RVI[3]) / 6

No lookahead: all rolling/SMA/shift terms use only bars through i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RVI_LEN = 10


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    raw = np.where(rng == 0, 0.0, (df["c"] - df["o"]) / rng.replace(0, np.nan))
    raw = pd.Series(raw, index=df.index).fillna(0.0)
    rvi = raw.rolling(RVI_LEN, min_periods=RVI_LEN).mean()
    signal = (rvi + 2 * rvi.shift(1) + 2 * rvi.shift(2) + rvi.shift(3)) / 6
    df["rvi_raw"] = raw
    df["rvi"] = rvi
    df["rvi_signal"] = signal
    return df
