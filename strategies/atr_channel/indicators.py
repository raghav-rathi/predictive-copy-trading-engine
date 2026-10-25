"""ATR channel breakout — SMA(20) plus/minus 1.5x ATR(14).

The channel adapts to volatility: in quiet markets the bands hug
price, in wild markets they widen. A close outside the channel is
treated as a genuine volatility-adjusted breakout, not noise.

Columns:
    chan_mid   -- SMA(20) of close
    chan_upper -- mid + 1.5 * ATR(14)
    chan_lower -- mid - 1.5 * ATR(14)
    atr        -- Wilder ATR(14)

Distinct from the Keltner strategies already in the library (which
use an EMA midline): this channel is SMA-based, the original
Wilder-style ATR band construction. No lookahead: SMA and ATR are
trailing.
"""

import numpy as np
import pandas as pd

from strategies import base as B

MID_N = 20
ATR_N = 14
ATR_MULT = 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr = B.atr(df["h"], df["l"], df["c"], ATR_N)
    mid = B.sma(df["c"], MID_N)
    df["chan_mid"] = mid
    df["chan_upper"] = mid + ATR_MULT * atr
    df["chan_lower"] = mid - ATR_MULT * atr
    df["atr"] = atr
    return df
