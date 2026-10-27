"""Elder Market Thermometer: range quietness as a reversal setup.

therm = today's high-low range / SMA(20) of range. Elder's
thermometer reads market emotion: high readings are emotional
extremes, low readings are calm. This build trades the calm print
*after* a trend: a quiet bar (therm < 0.6) with price still on the
trend's side of its 20-bar average and a close in the reversal
direction. It is a setup filter, not a standalone oscillator.
Columns: therm, sma20, atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    avg = rng.rolling(20, min_periods=20).mean()
    df["therm"] = rng / avg.replace(0, np.nan)
    df["sma20"] = df["c"].rolling(20, min_periods=20).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
