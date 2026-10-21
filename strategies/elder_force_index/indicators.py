"""Force Index indicators (Alexander Elder, "Trading for a Living", 1993).

Force Index = (close - close.shift(1)) * volume. It multiplies the price
change by volume, so it measures the force behind a move: big price change
on big volume = strong force; price drifting on thin volume = weak.

Elder's two-EMA setup:
  * fi2  = EMA(FI, 2)  — entry timer: fast enough to dip on the pullback
  * fi13 = EMA(FI, 13) — trend gauge: sign says who is in charge
All values on bar i use bars through i's close only (no lookahead).
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST_LEN = 2
TREND_LEN = 13
ATR_LEN = 14


def add_indicators(
    df: pd.DataFrame,
    fast_len: int = FAST_LEN,
    trend_len: int = TREND_LEN,
    atr_len: int = ATR_LEN,
) -> pd.DataFrame:
    df = df.copy()
    fi = (df["c"].diff().fillna(0.0)) * df["v"]
    df["force_index"] = fi
    df["fi2"] = B.ema(fi, fast_len)
    df["fi13"] = B.ema(fi, trend_len)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_len)
    df.attrs["trend_len"] = trend_len
    return df
