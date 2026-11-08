"""Outside-bar reversal indicators.

An outside bar engulfs the previous bar: h > prev h AND l < prev l.
ob_close_pos is the position of the close inside the bar's own range
(0 = low, 1 = high). sma20 is the 20-bar simple moving average of
close; vol_avg20 is the 20-bar average volume over the trailing 20
completed bars. All quantities use only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies.base import sma

SMA_BARS = 20
VOL_AVG_BARS = 20

INDICATOR_COLS = [
    "ob_sma20",
    "ob_vol_avg20",
    "ob_is_outside",
    "ob_close_pos",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ob_sma20"] = sma(df["c"], SMA_BARS)
    df["ob_vol_avg20"] = df["v"].shift(1).rolling(VOL_AVG_BARS, min_periods=VOL_AVG_BARS).mean()
    prev_h = df["h"].shift(1)
    prev_l = df["l"].shift(1)
    df["ob_is_outside"] = ((df["h"] > prev_h) & (df["l"] < prev_l)).fillna(False).astype(bool)
    rng = df["h"] - df["l"]
    df["ob_close_pos"] = np.where(rng > 0, (df["c"] - df["l"]) / rng.replace(0, np.nan), 0.5)
    return df
