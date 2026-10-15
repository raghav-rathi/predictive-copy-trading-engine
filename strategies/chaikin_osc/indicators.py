"""Chaikin Oscillator indicators (Marc Chaikin).

Money Flow Volume = CLV * volume, where
  CLV = ((close - low) - (high - close)) / (high - low)
ADL = cumulative MFV. Chaikin Oscillator = EMA(ADL, 3) - EMA(ADL, 10):
the momentum of money flow. Degenerate bars (H == L) contribute 0.
No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST_EMA = 3
SLOW_EMA = 10


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    rng = (h - l).replace(0.0, np.nan)
    clv = (((c - l) - (h - c)) / rng).fillna(0.0)
    df["adl"] = (clv * v).cumsum()
    df["chaikin_osc"] = B.ema(df["adl"], FAST_EMA) - B.ema(df["adl"], SLOW_EMA)
    return df
