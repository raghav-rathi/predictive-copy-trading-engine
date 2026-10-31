"""Choppiness Index (Dreiss, 14) + prior-bar Donchian(20) bands.

CHOP(14) = 100 * log10( sum(TR, 14) / (MaxHi14 - MinLo14) ) / log10(14),
where TR is the true range, MaxHi14 / MinLo14 are the highest high /
lowest low over 14 bars. A bar whose window range is zero (flat prices)
emits NaN rather than dividing by zero.

Donchian bands use only completed bars: the rolling 20-bar max high /
min low are shifted by 1, so the band on bar i covers bars i-20..i-1.
All columns are strictly causal.

Columns:
    chop            -- Choppiness Index, 0-100 scale (NaN until 14 bars)
    donchian_high   -- prior-bar Donchian(20) high band
    donchian_low    -- prior-bar Donchian(20) low band
    atr             -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

CHOP_PERIOD = 14
DONCHIAN_PERIOD = 20
TREND_LEVEL = 38.2
CHOPPY_LEVEL = 61.8


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tr = B.true_range(df["h"], df["l"], df["c"])
    sum_tr = tr.rolling(CHOP_PERIOD, min_periods=CHOP_PERIOD).sum()
    max_hi = df["h"].rolling(CHOP_PERIOD, min_periods=CHOP_PERIOD).max()
    min_lo = df["l"].rolling(CHOP_PERIOD, min_periods=CHOP_PERIOD).min()
    window_range = max_hi - min_lo
    ratio = sum_tr / window_range.replace(0, np.nan)
    chop = 100 * np.log10(ratio) / np.log10(CHOP_PERIOD)
    # log10 of a non-positive ratio is undefined; guard it to NaN.
    chop = chop.where((ratio > 0) & np.isfinite(ratio))
    df["chop"] = chop
    don = B.donchian(df["h"], df["l"], DONCHIAN_PERIOD)
    df["donchian_high"] = don[f"donchian_high_{DONCHIAN_PERIOD}"].shift(1)
    df["donchian_low"] = don[f"donchian_low_{DONCHIAN_PERIOD}"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
