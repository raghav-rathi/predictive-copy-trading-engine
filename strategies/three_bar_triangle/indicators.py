"""Raschke 3-bar triangle indicators.

Contraction bar (Raschke's definition): bar i has
h[i] < max(h[i-1], h[i-2]) AND l[i] > min(l[i-1], l[i-2])
— "high below two day high and low above two day low".
Triangle high = max(h[i-2], h[i-1], h[i]); triangle low =
min(l[i-2], l[i-1], l[i]). The triangle levels are forward-filled
for 5 bars after the contraction bar (a new contraction inside
the window restarts the triangle and the 5-bar clock); NaN
otherwise. The contraction bar itself can never trigger an entry
(its close is inside its own triangle), so entries effectively
occur on bars c+1..c+5.

Columns:
    contraction -- True on a contraction bar
    tri_high / tri_low -- triangle levels, valid 5 bars after a
        contraction, NaN otherwise
    vol_ma20 -- SMA(volume, 20)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
(the forward-fill only carries past contraction levels forward).
"""

import numpy as np
import pandas as pd

from strategies import base as B

VOL_MA = 20
VOL_MULT = 1.25
TRIANGLE_BARS = 5

INDICATOR_COLS = ["contraction", "tri_high", "tri_low", "vol_ma20", "atr"]


def add_indicators(df: pd.DataFrame, vol_ma: int = VOL_MA,
                   vol_mult: float = VOL_MULT,
                   triangle_bars: int = TRIANGLE_BARS) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    prev2_high = pd.concat([h.shift(1), h.shift(2)], axis=1).max(axis=1)
    prev2_low = pd.concat([l.shift(1), l.shift(2)], axis=1).min(axis=1)
    df["contraction"] = ((h < prev2_high) & (l > prev2_low)).fillna(False).astype(bool)
    tri_high_raw = pd.Series(np.where(
        df["contraction"],
        pd.concat([h, h.shift(1), h.shift(2)], axis=1).max(axis=1),
        np.nan), index=df.index)
    tri_low_raw = pd.Series(np.where(
        df["contraction"],
        pd.concat([l, l.shift(1), l.shift(2)], axis=1).min(axis=1),
        np.nan), index=df.index)
    # Bars since the latest contraction (forward-filled bar numbers).
    idx = pd.Series(np.where(df["contraction"], np.arange(len(df)), np.nan),
                    index=df.index)
    age = np.arange(len(df)) - idx.ffill()
    valid = (age <= triangle_bars) & (age >= 0)
    df["tri_high"] = tri_high_raw.ffill().where(valid)
    df["tri_low"] = tri_low_raw.ffill().where(valid)
    df["vol_ma20"] = B.sma(df["v"], vol_ma)
    df["atr"] = B.atr(h, l, df["c"], 14)
    return df
