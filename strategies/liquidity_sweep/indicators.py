"""Liquidity-sweep detectors (ICT / smart-money-concepts mechanics).

A sweep needs (a) a real pool: the highest high / lowest low of the last
LOOKBACK bars excluding the current bar, (b) a wick through it that is at
least MIN_WICK_ATR of an ATR beyond the level (filters trivial pokes),
and (c) a reclaim: the bar CLOSES back inside the level. A body close
beyond the level is a breakout, not a sweep. The sweep bar itself carries
the signal; the stop reference is the sweep extreme. All causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LOOKBACK = 20        # swing-extreme lookback (bars)
MIN_WICK_ATR = 0.25  # wick beyond the level must exceed this x ATR


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    atr_v = B.atr(h, l, c, 14)
    # pools: extremes of the prior LOOKBACK bars (shifted so the current
    # bar can never define its own level)
    pool_high = h.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).max()
    pool_low = l.shift(1).rolling(LOOKBACK, min_periods=LOOKBACK).min()
    wick_up = h - pool_high
    wick_dn = pool_low - l
    # sweep = wick through + meaningful size + close back inside
    sweep_up = (wick_up > MIN_WICK_ATR * atr_v) & (c < pool_high)
    sweep_dn = (wick_dn > MIN_WICK_ATR * atr_v) & (c > pool_low)
    df["sweep_up"] = sweep_up.fillna(False)
    df["sweep_dn"] = sweep_dn.fillna(False)
    df["sweep_wick_atr"] = np.where(
        sweep_up.fillna(False), wick_up / atr_v.replace(0, np.nan),
        np.where(sweep_dn.fillna(False), wick_dn / atr_v.replace(0, np.nan), 0.0),
    )
    df["pool_high"] = pool_high
    df["pool_low"] = pool_low
    return df
