"""Center of Gravity oscillator indicators (John Ehlers).

The center of gravity of the last 10 closes is the price-weighted
centroid: recent closes get weight 1, the oldest gets weight 10.
Subtracting the centroid's position from the window midpoint (5.5)
centers the oscillator at zero: positive when recent prices sit above
the window's center of mass (uptrend bias), negative when below.
Ehlers' trigger line is the SMA of the CG itself.

Columns:
    cg         -- 5.5 - sum((10-j) * close_j) / sum(close) over the
                  last 10 closes (j = 0 oldest, 9 newest)
    cg_trigger -- SMA(3) of cg
    atr        -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 10
TRIGGER = 3


def _cg(window):
    weights = np.arange(PERIOD, 0, -1, dtype=float)  # oldest heaviest
    return (PERIOD + 1) / 2.0 - float(np.dot(window, weights) / window.sum())


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["cg"] = df["c"].rolling(PERIOD, min_periods=PERIOD).apply(_cg, raw=True)
    df["cg_trigger"] = B.sma(df["cg"], TRIGGER)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
