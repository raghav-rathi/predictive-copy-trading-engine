"""Outside-bar reversal signals.

Bullish outside reversal: the bar before the outside bar closed below
SMA(20) (prior downtrend), the outside bar closes in the upper third
of its own range, and volume is above its 20-bar average -> long.
Bearish mirror: prior close above SMA(20), outside bar closes in the
lower third, volume above average -> short.

Exit: a long exits on a bearish outside bar (outside bar closing in
its lower third) or on a close below the low of the most recent
outside bar as of the prior bar (the entry outside bar's low while no
newer outside bar has formed); mirror for shorts. Signals on bar i
use only data through bar i's close.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    v = df["v"]
    outside = df["ob_is_outside"]
    pos = df["ob_close_pos"]
    sma_prev = df["ob_sma20"].shift(1)
    c_prev = c.shift(1)
    vol_ok = (v > df["ob_vol_avg20"]).fillna(False)
    bull_rev = (outside & (c_prev < sma_prev) & (pos >= 2.0 / 3.0)).fillna(False)
    bear_rev = (outside & (c_prev > sma_prev) & (pos <= 1.0 / 3.0)).fillna(False)
    df["long_entry"] = (bull_rev & vol_ok).astype(bool)
    df["short_entry"] = (bear_rev & vol_ok).astype(bool)
    # Low/high of the most recent outside bar, as of the prior bar.
    ob_low = df["l"].where(outside).ffill().shift(1)
    ob_high = df["h"].where(outside).ffill().shift(1)
    df["long_exit"] = (bear_rev | (c < ob_low)).fillna(False).astype(bool)
    df["short_exit"] = (bull_rev | (c > ob_high)).fillna(False).astype(bool)
    return df
