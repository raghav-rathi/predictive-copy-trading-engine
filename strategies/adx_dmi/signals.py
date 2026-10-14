"""Wilder Directional Movement signals (ADX-filtered DI crosses).

long_entry  = +DI crosses above -DI while ADX(14) >= 25
short_entry = -DI crosses above +DI while ADX(14) >= 25
long_exit   = -DI crosses above +DI  OR  ADX(14) < 20 (trend faded)
short_exit  = +DI crosses above -DI  OR  ADX(14) < 20
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B
from strategies.adx_dmi import indicators as ind


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pdi, mdi, adx = df["plus_di"], df["minus_di"], df["adx"]
    strong = adx >= ind.ADX_ENTRY
    long_x = B.crossed_above(pdi, mdi)
    short_x = B.crossed_above(mdi, pdi)
    df["long_entry"] = long_x & strong
    df["short_entry"] = short_x & strong
    df["long_exit"] = short_x | (adx < ind.ADX_FADE)
    df["short_exit"] = long_x | (adx < ind.ADX_FADE)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
