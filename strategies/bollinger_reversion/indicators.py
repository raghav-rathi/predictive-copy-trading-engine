"""Bollinger Bands %b mean-reversion indicators.

Bollinger Bands(20, 2.0): middle = SMA(20) of close, upper/lower =
middle +/- 2 * rolling standard deviation (population std is NOT
used; pandas rolling std is the sample std, ddof=1, which is the
standard Bollinger construction). %b = (close - lower) /
(upper - lower): %b <= 0 means the close tagged or broke the lower
band, %b >= 1 the upper band.

Columns:
    bb_mid / bb_upper / bb_lower / bb_width -- bands (base.bollinger)
    pct_b -- %b position of the close inside the bands
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], BB_N, BB_K)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_width"] = bb["bb_width"]
    width = df["bb_upper"] - df["bb_lower"]
    df["pct_b"] = (df["c"] - df["bb_lower"]) / width.replace(0, np.nan)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
