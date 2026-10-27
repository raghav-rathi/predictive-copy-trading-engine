"""Volume Oscillator: (SMA(5) volume - SMA(10) volume) / SMA(10)
volume, in percent. Rising volume flow confirms the price trend;
the zero cross is the trigger and the 20-bar price average is the
trend filter, so a volume surge against the trend does not fire.
Columns: vol_osc, sma20, atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    short = df["v"].rolling(5, min_periods=5).mean()
    long = df["v"].rolling(10, min_periods=10).mean()
    df["vol_osc"] = 100 * (short - long) / long.replace(0, np.nan)
    df["sma20"] = df["c"].rolling(20, min_periods=20).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
