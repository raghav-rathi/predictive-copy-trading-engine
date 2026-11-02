"""Aroon Oscillator indicators (Tushar Chande).

Aroon-Up = 100 * (25 - bars since the 25-bar high) / 25; Aroon-Down
is the mirror image on lows. The oscillator is their difference:
+100 in a fresh uptrend, -100 in a fresh downtrend, near 0 in chop.

Columns:
    aroon_up, aroon_down, aroon_osc, atr

All windows use only bars up to and including the current bar.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 25


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def _since(s, fn):
        return s.rolling(PERIOD).apply(lambda x: (PERIOD - 1) - fn(x), raw=True)

    since_high = _since(df["h"], np.argmax)
    since_low = _since(df["l"], np.argmin)
    df["aroon_up"] = 100.0 * (PERIOD - since_high) / PERIOD
    df["aroon_down"] = 100.0 * (PERIOD - since_low) / PERIOD
    df["aroon_osc"] = df["aroon_up"] - df["aroon_down"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
