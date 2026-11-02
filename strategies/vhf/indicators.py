"""Vertical Horizontal Filter (Adam White, 1991).

VHF = (highest high - lowest low over 28 bars) / sum of absolute
close-to-close changes over 28 bars. A value near 1 means price
moved in one direction (trend); near 0 means it travelled a lot
to go nowhere (range). VHF gives regime, not direction — the
SMA(28) supplies direction.

Columns:
    vhf, sma28, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 28


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(PERIOD).max()
    ll = df["l"].rolling(PERIOD).min()
    chg = df["c"].diff().abs().rolling(PERIOD).sum()
    df["vhf"] = (hh - ll) / chg.replace(0, np.nan)
    df["sma28"] = B.sma(df["c"], PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
