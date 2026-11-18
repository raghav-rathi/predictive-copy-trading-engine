"""ATR expansion breakout indicators.

atr14 = ATR(14); atr_ma20 = SMA(20) of atr14; range_high / range_low
= 20-bar max / min of the CLOSE, shifted by 1 (previous 20 bars
only); range_width = range_high - range_low; range_ok = the range
is tight, range_width <= 2.0 * atr14.

Columns:
    atr            -- Wilder ATR(14)
    atr_ma20       -- SMA(20) of atr14
    range_high_20  -- max close of the previous 20 bars
    range_low_20   -- min close of the previous 20 bars
    range_ok       -- range_width <= 2.0 * atr14

No lookahead: every value on bar i uses data through bar i's close.
The range levels exclude the current bar (shift(1)): a close can
only break a level that does not already include it.
"""

import pandas as pd

from strategies import base as B

ATR_N = 14
ATR_MA_N = 20
RANGE_N = 20
RANGE_ATR_MULT = 2.0

INDICATOR_COLS = ["atr", "atr_ma20", "range_high_20", "range_low_20",
                  "range_ok"]


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N,
                   atr_ma_n: int = ATR_MA_N, range_n: int = RANGE_N,
                   range_mult: float = RANGE_ATR_MULT) -> pd.DataFrame:
    df = df.copy()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["atr_ma20"] = B.sma(df["atr"], atr_ma_n)
    df["range_high_20"] = df["c"].rolling(range_n, min_periods=range_n).max().shift(1)
    df["range_low_20"] = df["c"].rolling(range_n, min_periods=range_n).min().shift(1)
    range_width = df["range_high_20"] - df["range_low_20"]
    df["range_ok"] = (range_width <= range_mult * df["atr"]).fillna(False)
    return df
