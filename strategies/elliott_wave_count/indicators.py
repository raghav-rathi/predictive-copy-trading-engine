"""Elliott wave pivot scaffolding.

A 5-bar pivot (2 bars each side) marks a swing high/low.  The pivot is
only *confirmed* 2 bars after the extreme bar, so the pivot price is
recorded on the confirmation bar -- no lookahead: the value on row i
uses bars through i only.  The wave-count state machine in signals.py
walks these pivots in order.

    swing_high -- price of the confirmed swing high, NaN elsewhere
    swing_low  -- price of the confirmed swing low, NaN elsewhere
    atr        -- Wilder ATR(14) for the risk layer

Source: Elliott Wave Theory --
https://www.rabofund.com/blogs/what-is-elliott-wave-theory-a-practical-guide-for-forex-traders
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_N = 5  # shipped default: 2 bars each side


def _pivots(h: pd.Series, l: pd.Series, pivot_n: int):
    """Strict 5-bar pivots, recorded on the confirmation bar.

    The pivot bar k is confirmed at bar k + half: the value on row i
    is the price of bar i - half, and only if that bar's high is
    *strictly* above (low strictly below) every other bar in the
    window -- ties never count as pivots, so flat stretches are quiet.
    """
    half = pivot_n // 2
    shifts = [half + j for j in range(-half, half + 1) if j != 0]
    others_max = pd.concat([h.shift(s) for s in shifts], axis=1).max(axis=1)
    others_min = pd.concat([l.shift(s) for s in shifts], axis=1).min(axis=1)
    sh = np.where(h.shift(half) > others_max, h.shift(half), np.nan)
    sl = np.where(l.shift(half) < others_min, l.shift(half), np.nan)
    return sh, sl


def add_indicators(df: pd.DataFrame, pivot_n: int = PIVOT_N) -> pd.DataFrame:
    df = df.copy()
    h, l = df["h"], df["l"]
    sh, sl = _pivots(h, l, pivot_n)
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
