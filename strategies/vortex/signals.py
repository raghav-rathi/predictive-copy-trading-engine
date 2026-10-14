"""Vortex signals.

Long  on VI+ crossing above VI-, gated by ADX(14) > threshold (optional filter).
Short on VI- crossing above VI+ (VI+ crossing below VI-), same gate.
Exit on the opposite cross (ungated: exits are always taken).

The ADX filter is parameterizable (adx_filter=True/False, adx_th=...) so
the filtered vs unfiltered variants and gate levels can be backtested
head-to-head.
"""

import pandas as pd

from strategies import base as B
from strategies.vortex.indicators import ADX_THRESHOLD


def add_signals(
    df: pd.DataFrame, adx_filter: bool = True, adx_th: float = ADX_THRESHOLD
) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["vi_plus"], df["vi_minus"]).fillna(False)
    cross_dn = B.crossed_below(df["vi_plus"], df["vi_minus"]).fillna(False)
    regime = df["adx"] > adx_th if adx_filter else True
    df["long_entry"] = cross_up & regime
    df["short_entry"] = cross_dn & regime
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
