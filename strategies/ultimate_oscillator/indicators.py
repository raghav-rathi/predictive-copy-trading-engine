"""Larry Williams' Ultimate Oscillator (UO).

From "The Ultimate Oscillator" (Technical Analysis of Stocks &
Commodities, April 1985). Williams designed UO to fix the
false-divergence problem of single-window momentum oscillators by
blending three timeframes with 4:2:1 weights.

Formulas (Wikipedia / Fidelity):

    prev_c = c.shift(1)
    BP     = c - min(l, prev_c)            # buying pressure
    TR     = max(h, prev_c) - min(l, prev_c)  # Williams' true range
    avg7   = sum(BP, 7) / sum(TR, 7)
    avg14  = sum(BP, 14) / sum(TR, 14)
    avg28  = sum(BP, 28) / sum(TR, 28)
    UO     = 100 * (4*avg7 + 2*avg14 + avg28) / 7

Range 0-100 by construction (0 <= BP <= TR at every bar). No
lookahead: the rolling sums at bar j use data through bar j only.

Columns added by add_indicators:

    uo   -- Ultimate Oscillator, 0-100 (50.0 on degenerate 0/0 bars)
    atr  -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

N_FAST, N_MID, N_SLOW = 7, 14, 28          # fixed a priori (Williams)
W_FAST, W_MID, W_SLOW = 4.0, 2.0, 1.0     # fixed a priori (Williams)


def buying_pressure(c: pd.Series, l: pd.Series) -> pd.Series:
    """BP = c - min(l, prev_c)."""
    prev_c = c.shift(1)
    return (c - pd.concat([l, prev_c], axis=1).min(axis=1)).rename("bp")


def true_range_williams(h: pd.Series, l: pd.Series, c: pd.Series) -> pd.Series:
    """Williams' TR = max(h, prev_c) - min(l, prev_c)."""
    prev_c = c.shift(1)
    hi = pd.concat([h, prev_c], axis=1).max(axis=1)
    lo = pd.concat([l, prev_c], axis=1).min(axis=1)
    return (hi - lo).rename("tr")


def ultimate_oscillator(h: pd.Series, l: pd.Series, c: pd.Series,
                        n1: int = N_FAST, n2: int = N_MID, n3: int = N_SLOW,
                        w1: float = W_FAST, w2: float = W_MID, w3: float = W_SLOW) -> pd.Series:
    """Ultimate Oscillator of the OHLC series, 0-100."""
    bp = buying_pressure(c, l)
    tr = true_range_williams(h, l, c)

    def _avg(n: int) -> pd.Series:
        num = bp.rolling(n, min_periods=n).sum()
        den = tr.rolling(n, min_periods=n).sum()
        return num / den.replace(0.0, np.nan)

    uo = 100.0 * (w1 * _avg(n1) + w2 * _avg(n2) + w3 * _avg(n3)) / (w1 + w2 + w3)
    # Degenerate bars (TR sum == 0, e.g. a flat tape) give 0/0 -> neutral 50.
    # clip() guards float dust outside [0, 100].
    return uo.fillna(50.0).clip(0.0, 100.0).rename("uo")


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["uo"] = ultimate_oscillator(df["h"], df["l"], df["c"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
