"""Choppiness Index indicators (E.W. Dreiss).

CHOP(n) = 100 * log10( sum(TR,1,n) / (HH(n) - LL(n)) ) / log10(n).
CHOP -> 100 means maximum chop (the bar-to-bar ranges fill the whole
n-bar range: sideways). CHOP -> 0 means the n-bar range was covered in
a straight line (trend). Regime gates: trending when CHOP < 38.2,
choppy when CHOP > 61.8 (the classic Dreiss thresholds). Donchian(20)
breakouts supply the directional entries, taken only in the trending
regime. All causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CHOP_N = 14
TREND_MAX = 38.2
CHOP_MIN = 61.8
DONCHIAN_N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    tr = B.true_range(h, l, c)
    hh = h.rolling(CHOP_N, min_periods=CHOP_N).max()
    ll = l.rolling(CHOP_N, min_periods=CHOP_N).min()
    tr_sum = tr.rolling(CHOP_N, min_periods=CHOP_N).sum()
    rng = (hh - ll).replace(0, np.nan)
    with np.errstate(divide="ignore", invalid="ignore"):
        chop = 100.0 * np.log10(tr_sum / rng) / np.log10(CHOP_N)
    df["chop"] = chop.clip(0, 100)
    df["trending"] = (chop < TREND_MAX).fillna(False)
    df["choppy"] = (chop > CHOP_MIN).fillna(False)
    dc = B.donchian(h, l, DONCHIAN_N)
    df[f"dc_high_{DONCHIAN_N}"] = dc[f"donchian_high_{DONCHIAN_N}"]
    df[f"dc_low_{DONCHIAN_N}"] = dc[f"donchian_low_{DONCHIAN_N}"]
    df["dc_mid"] = (df[f"dc_high_{DONCHIAN_N}"] + df[f"dc_low_{DONCHIAN_N}"]) / 2
    return df
