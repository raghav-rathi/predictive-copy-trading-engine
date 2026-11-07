"""Bill Williams fractal breakout + Alligator filter indicators.

Fractals (k=2): an up-fractal is a bar whose high is strictly the
highest of the 2 bars on each side; a down-fractal mirrors on lows.
A fractal is only usable 2 bars after its extreme bar (confirmed),
so the confirmed level is the raw pivot shifted by 2 and
forward-filled — the level known on bar i is the pivot formed at bar
i-2. No lookahead.

Alligator: SMMA (Wilder smoothing) of the median price (h+l)/2 —
jaw 13, teeth 8, lips 5 — used UNSHIFTED, per the spec (the classic
Williams presentation shifts them forward 8/5/3 bars; this build does
not). "Awake, pointing up" = lips > teeth > jaw; the mirror for
shorts.
"""

import numpy as np
import pandas as pd

from strategies import base as B

JAW_LEN = 13
TEETH_LEN = 8
LIPS_LEN = 5
FRACTAL_K = 2

INDICATOR_COLS = [
    "alligator_jaw",
    "alligator_teeth",
    "alligator_lips",
    "gator_awake_long",
    "gator_awake_short",
    "fractal_buy_raw",
    "fractal_sell_raw",
    "frac_up_high",
    "frac_down_low",
]


def _smma(s: pd.Series, n: int) -> pd.Series:
    """Wilder-style smoothed moving average."""
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    jaw = _smma(median, JAW_LEN)
    teeth = _smma(median, TEETH_LEN)
    lips = _smma(median, LIPS_LEN)
    df["alligator_jaw"] = jaw
    df["alligator_teeth"] = teeth
    df["alligator_lips"] = lips
    df["gator_awake_long"] = ((lips > teeth) & (teeth > jaw)).fillna(False)
    df["gator_awake_short"] = ((lips < teeth) & (teeth < jaw)).fillna(False)

    h, l = df["h"], df["l"]
    k = FRACTAL_K
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
    # Pivot at bar i is confirmed at bar i+k: shift by k so the level
    # on bar i only uses pivots formed at/before bar i-k.
    df["frac_up_high"] = h.where(is_buy).shift(k).ffill()
    df["frac_down_low"] = l.where(is_sell).shift(k).ffill()
    return df
