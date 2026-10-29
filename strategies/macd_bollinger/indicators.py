"""Bollinger Bands applied to the MACD line (Carter-style).

MACD = EMA(12) - EMA(26), signal = EMA(9) of the MACD line, from
strategies.base.macd. Bollinger Bands (SMA(20), +/-2 SD) are then
computed on the MACD line itself, not on price — the classic
"Carter" setup (John Carter, Mastering the Trade) in which the
MACD line's excursion outside its own bands marks an overextended
move, and the cross back inside the band marks the release.

Columns:
    macd            -- MACD line (EMA12 - EMA26)
    macd_signal     -- EMA(9) of the MACD line
    macd_hist       -- macd - macd_signal
    macd_bb_mid     -- SMA(20) of the MACD line
    macd_bb_upper   -- mid + 2 * SD(20) of the MACD line
    macd_bb_lower   -- mid - 2 * SD(20) of the MACD line
    macd_bb_width   -- upper - lower
    atr             -- Wilder ATR(14) for the risk layer

No lookahead: every window is trailing (min_periods=n), so the
bands at bar i use only MACD values through bar i.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9
BB_N = 20
BB_K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    m = B.macd(df["c"], FAST, SLOW, SIGNAL)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    mid = df["macd"].rolling(BB_N, min_periods=BB_N).mean()
    sd = df["macd"].rolling(BB_N, min_periods=BB_N).std()
    df["macd_bb_mid"] = mid
    df["macd_bb_upper"] = mid + BB_K * sd
    df["macd_bb_lower"] = mid - BB_K * sd
    df["macd_bb_width"] = 2 * BB_K * sd
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
