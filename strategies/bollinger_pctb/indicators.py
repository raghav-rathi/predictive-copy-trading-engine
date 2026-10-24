"""Bollinger %B indicators (John Bollinger, Bollinger on Bollinger Bands).

    bb_mid    = SMA(close, 20)
    bb_upper  = bb_mid + 2.0 * SD(close, 20)
    bb_lower  = bb_mid - 2.0 * SD(close, 20)
    pctb      = (close - bb_lower) / (bb_upper - bb_lower)

%B locates price inside its own Bollinger Band: 0 at the lower band,
0.5 at the middle band, 1 at the upper band, above 1 / below 0
outside the bands. A zero-width band (all 20 closes identical) makes
the ratio undefined; there %B is defined as 0.5 (price sits exactly
on the collapsed band), which is the only value consistent with the
band geometry.

Columns:

    bb_mid, bb_upper, bb_lower, bb_width -- Bollinger Band(20, 2.0)
    pctb   -- Bollinger %B
    atr    -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20        # shipped default (fixed a priori)
BB_K = 2.0       # band width in standard deviations


def add_indicators(df: pd.DataFrame, n: int = BB_N,
                   k: float = BB_K) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], n, k)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_width"] = bb["bb_width"]
    width = df["bb_upper"] - df["bb_lower"]
    pctb = (df["c"] - df["bb_lower"]) / width
    # Zero-width band -> price is on the collapsed band -> %B = 0.5.
    pctb = pctb.where(width > 0, 0.5)
    pctb = pctb.replace([np.inf, -np.inf], np.nan)
    df["pctb"] = pctb
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
