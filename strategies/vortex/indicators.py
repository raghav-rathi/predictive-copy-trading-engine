"""Vortex Indicator (VI) -- Botes & Siepman, TASC Jan 2010.

Positive/negative vortex movement over a lookback n (default 14):

    VM+  = |h - l.shift(1)|          (upward movement)
    VM-  = |l - h.shift(1)|          (downward movement)
    VI+  = sum_n(VM+) / sum_n(TR)    (VI- likewise)
    TR   = base.true_range(h, l, c)

VI+ above VI- = buying pressure dominates the window; a VI+ crossing
above VI- is the long trigger in the original paper, and vice versa.
Columns:

    vi_pos   -- VI+(n)
    vi_neg   -- VI-(n)
    vi_spread -- vi_pos - vi_neg (signed pressure)
    atr      -- Wilder ATR(14) for the risk layer

No lookahead: every rolling sum on bar j uses bars through j only;
min_periods=n so the first n-1 bars are NaN (never partially formed).
Division guards against a zero TR sum (flat synthetic bars) with a
masked NaN.
"""

import numpy as np
import pandas as pd

from strategies import base as B

VORTEX_N = 14  # shipped default


def vortex(h: pd.Series, l: pd.Series, c: pd.Series, n: int = VORTEX_N) -> pd.DataFrame:
    """Return vi_pos / vi_neg for the Vortex Indicator with window n."""
    vm_pos = (h - l.shift(1)).abs()
    vm_neg = (l - h.shift(1)).abs()
    tr = B.true_range(h, l, c)
    sum_pos = vm_pos.rolling(n, min_periods=n).sum()
    sum_neg = vm_neg.rolling(n, min_periods=n).sum()
    sum_tr = tr.rolling(n, min_periods=n).sum()
    safe = sum_tr.replace(0.0, np.nan)
    vi_pos = sum_pos / safe
    vi_neg = sum_neg / safe
    return pd.DataFrame({"vi_pos": vi_pos, "vi_neg": vi_neg})


def add_indicators(df: pd.DataFrame, n: int = VORTEX_N) -> pd.DataFrame:
    df = df.copy()
    v = vortex(df["h"], df["l"], df["c"], n)
    df["vi_pos"] = v["vi_pos"]
    df["vi_neg"] = v["vi_neg"]
    df["vi_spread"] = v["vi_pos"] - v["vi_neg"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
