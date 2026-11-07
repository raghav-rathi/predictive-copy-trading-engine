"""Bollinger Band squeeze breakout indicators (John Bollinger).

BB(20, 2): mid = SMA(20), bands = mid +/- 2 * std(20). BandWidth =
(upper - lower) / mid. A squeeze is a BandWidth in the lowest 15% of
the last 50 bars (percentile rank within the window, ties ranked
lowest so a dead-flat band counts as squeezed). The squeeze flag is
forwarded so an entry is armed for 10 bars after a squeeze ends —
breakouts usually fire as the bands start expanding again. All values
use only data through the current bar's close — no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_LEN = 20
BB_K = 2.0
SQUEEZE_LOOKBACK = 50
SQUEEZE_PCT = 0.15
SQUEEZE_ARM_BARS = 10

INDICATOR_COLS = [
    "bb_mid",
    "bb_upper",
    "bb_lower",
    "bb_width",
    "bb_bandwidth",
    "bb_squeeze",
    "bb_squeeze_armed",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], BB_LEN, BB_K)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_width"] = bb["bb_width"]
    df["bb_bandwidth"] = bb["bb_width"] / bb["bb_mid"]
    bw = df["bb_bandwidth"]
    rank = bw.rolling(SQUEEZE_LOOKBACK, min_periods=20).rank(
        pct=True, method="min"
    )
    squeeze = (rank <= SQUEEZE_PCT).fillna(False)
    df["bb_squeeze"] = squeeze
    armed = squeeze.rolling(SQUEEZE_ARM_BARS + 1, min_periods=1).max() > 0
    df["bb_squeeze_armed"] = armed.fillna(False)
    return df
