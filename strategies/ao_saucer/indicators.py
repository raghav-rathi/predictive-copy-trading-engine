"""Bill Williams Awesome Oscillator (AO) Saucer indicators.

    median -- (h + l) / 2
    ao     -- SMA(median, 5) - SMA(median, 34)
    atr14  -- Wilder ATR(14) for risk

No lookahead: both SMAs are trailing only; ATR is Wilder
smoothing.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST_N = 5
SLOW_N = 34
ATR_N = 14


def add_indicators(
    df: pd.DataFrame,
    fast_n: int = FAST_N,
    slow_n: int = SLOW_N,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    df["median"] = median
    df["ao"] = B.sma(median, fast_n) - B.sma(median, slow_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
