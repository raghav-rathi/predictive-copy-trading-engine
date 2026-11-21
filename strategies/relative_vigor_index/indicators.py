"""John Ehlers Relative Vigor Index indicators.

RVI numerator = (c-o) + 2*(c1-o1) + 2*(c2-o2) + (c3-o3), where
c1/o1 are one bar back, etc. Denominator = (h-l) + 2*(h1-l1) +
2*(h2-l2) + (h3-l3). RVI = numerator / denominator (a zero
denominator gives 0). Signal = 4-bar weighted average of RVI:
(RVI + 2*RVI1 + 2*RVI2 + RVI3) / 6.

Columns:
    rvi_num / rvi_den -- the 1-2-2-1 weighted numerator/denominator
    rvi -- Relative Vigor Index
    rvi_signal -- 4-bar weighted signal line
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only (trailing 4-bar windows).

NOTE: this is the direct 4-bar SWMA ratio from the brief. Some
platform implementations additionally average the numerator and
denominator over 10 bars before dividing (RVI = SMA(Numerator, 10)
/ SMA(Denominator, 10)); that variant is NOT used here — see
CALIBRATION.md.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    h = df["h"]
    l = df["l"]
    c = df["c"]

    co = c - o
    hl = h - l
    num = co + 2 * co.shift(1) + 2 * co.shift(2) + co.shift(3)
    den = hl + 2 * hl.shift(1) + 2 * hl.shift(2) + hl.shift(3)
    df["rvi_num"] = num
    df["rvi_den"] = den
    rvi = num / den
    # Zero denominator -> 0 (also kills +/-inf); NaN denominator (first
    # 3 bars) stays NaN because (den == 0) is False for NaN.
    rvi = rvi.mask(den == 0, 0.0)
    df["rvi"] = rvi
    df["rvi_signal"] = (
        rvi + 2 * rvi.shift(1) + 2 * rvi.shift(2) + rvi.shift(3)
    ) / 6.0
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
