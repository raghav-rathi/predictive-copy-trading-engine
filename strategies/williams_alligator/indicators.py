"""Bill Williams' Alligator + fractal breakout indicators ("Trading Chaos").

Alligator lines on median price (h+l)/2, SMMA = Wilder smoothing
(alpha = 1/n EWM):
  * jaw   = SMMA(13) of median, known with an 8-bar lag
  * teeth = SMMA(8)  of median, known with a 5-bar lag
  * lips  = SMMA(5)  of median, known with a 3-bar lag

The shift means the value on bar i is computed from median data through
bar i-shift only — no lookahead. "Awake" (trending) = lines fanned and
ordered: lips > teeth > jaw for longs, lips < teeth < jaw for shorts.

Fractals (k=2): a buy fractal is a strict 5-bar high pivot
(high[i] > max of the 2 bars on each side). The pivot at bar i is only
confirmed at bar i+2, so the confirmed level is the raw pivot shifted by
k bars and forward-filled — the level known on bar i is the pivot formed
at bar i-k. Sell fractal mirrors on lows.
"""

import numpy as np
import pandas as pd

from strategies import base as B

JAW_LEN = 13
JAW_SHIFT = 8
TEETH_LEN = 8
TEETH_SHIFT = 5
LIPS_LEN = 5
LIPS_SHIFT = 3
FRACTAL_K = 2


def smma(s: pd.Series, n: int) -> pd.Series:
    """Wilder-style smoothed moving average."""
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def add_indicators(
    df: pd.DataFrame,
    jaw_len: int = JAW_LEN,
    jaw_shift: int = JAW_SHIFT,
    teeth_len: int = TEETH_LEN,
    teeth_shift: int = TEETH_SHIFT,
    lips_len: int = LIPS_LEN,
    lips_shift: int = LIPS_SHIFT,
    fractal_k: int = FRACTAL_K,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    jaw = smma(median, jaw_len).shift(jaw_shift)
    teeth = smma(median, teeth_len).shift(teeth_shift)
    lips = smma(median, lips_len).shift(lips_shift)
    df["alligator_jaw"] = jaw
    df["alligator_teeth"] = teeth
    df["alligator_lips"] = lips
    df["gator_awake_long"] = ((lips > teeth) & (teeth > jaw)).fillna(False)
    df["gator_awake_short"] = ((lips < teeth) & (teeth < jaw)).fillna(False)

    h, l = df["h"], df["l"]
    k = fractal_k
    is_buy = (
        (h > h.shift(1))
        & (h > h.shift(k))
        & (h > h.shift(-1))
        & (h > h.shift(-k))
    )
    is_sell = (
        (l < l.shift(1))
        & (l < l.shift(k))
        & (l < l.shift(-1))
        & (l < l.shift(-k))
    )
    df["fractal_buy_raw"] = is_buy.fillna(False)
    df["fractal_sell_raw"] = is_sell.fillna(False)
    # pivot at bar i is confirmed at bar i+k: shift the raw pivots by k so
    # the level on bar i only uses pivots formed at/before bar i-k
    df["fractal_buy_level"] = h.where(is_buy).shift(k).ffill()
    df["fractal_sell_level"] = l.where(is_sell).shift(k).ffill()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
