"""On-Balance Volume trend indicators (Joseph Granville).

OBV accumulates signed volume: on up-close bars add the bar's volume,
on down-close bars subtract it, on unchanged bars add nothing.

    OBV(i) = OBV(i-1) + sign(c[i] - c[i-1]) * v[i]

Trend filter: EMA(50) of close. Confirmation: OBV above its own EMA(20)
and rising on a 3-bar slope. OBV is a cumulative level, so the EMA(20)
cross is what turns it into a usable timing signal -- the raw level is
never compared across assets. No lookahead: every bar uses only data
through that bar's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

TREND_EMA = 50
OBV_EMA = 20
SLOPE_BARS = 3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    signed = np.sign(df["c"].diff()).fillna(0.0) * df["v"]
    df["obv"] = signed.cumsum()
    df["ema50"] = B.ema(df["c"], TREND_EMA)
    df["obv_ema20"] = B.ema(df["obv"], OBV_EMA)
    df["obv_slope"] = df["obv"] - df["obv"].shift(SLOPE_BARS)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
