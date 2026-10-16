"""Episodic-pivot (crypto adaptation) indicators.

Bonde's episodic pivot is a neglect base (tight, low-volume coil) broken
by a high-volume, high-range thrust bar that closes near its high above
the base. Stocks use earnings as the catalyst; crypto has no earnings,
so this implementation proxies the catalyst with range expansion (>=2x
ATR) plus volume expansion (>=2x 50-bar mean) — treat results as the
proxy's, not the original's.

Adaptation note: Bonde's "tight base" (range <= ~1.2x ATR) is calibrated
for daily stock bars. On 1h crypto, a 30-bar range runs ~5.6x ATR at the
median (25th pct ~= 4.5x), so the hourly base uses tight_atr_mult=4.0 —
the bottom quartile of hourly coil tightness.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(
    df: pd.DataFrame,
    base_n: int = 30,
    atr_n: int = 14,
    tight_atr_mult: float = 4.0,  # hourly adaptation; daily original ~= 1.2
    dryup_mult: float = 0.8,
    thrust_range_mult: float = 2.0,
    thrust_vol_mult: float = 2.0,
    vol_sma_n: int = 50,
    close_pos_min: float = 0.7,
) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    rng = h - l
    atr = B.atr(h, l, c, atr_n)
    vol_sma = B.sma(v, vol_sma_n)

    # neglect base = the 30 bars ENDING one bar ago (no lookahead into bar i)
    base_h = h.rolling(base_n, min_periods=base_n).max().shift(1)
    base_l = l.rolling(base_n, min_periods=base_n).min().shift(1)
    base_atr_med = atr.rolling(base_n, min_periods=base_n).median().shift(1)
    base_vol = v.rolling(base_n, min_periods=base_n).mean().shift(1)
    prior_vol = v.rolling(base_n, min_periods=base_n).mean().shift(base_n + 1)

    tight = (base_h - base_l) <= tight_atr_mult * base_atr_med
    dryup = base_vol < dryup_mult * prior_vol

    with np.errstate(divide="ignore", invalid="ignore"):
        close_pos = (c - l) / rng.replace(0, np.nan)

    df["base_high"] = base_h
    df["thrust"] = (
        (rng >= thrust_range_mult * atr)
        & (v >= thrust_vol_mult * vol_sma)
        & (close_pos >= close_pos_min)
        & (c > base_h)
        & tight.fillna(False)
        & dryup.fillna(False)
    ).fillna(False).astype(bool)
    return df
