"""Wilder DMI indicators.

Wilder DMI(14): +DM/-DM and true range are Wilder-smoothed (alpha 1/14),
+DI = 100 x smoothed(+DM) / ATR, -DI = 100 x smoothed(-DM) / ATR,
DX = 100 x |+DI - -DI| / (+DI + -DI), ADX = Wilder-smoothed DX
(alpha 1/14). All smoothing is causal (EWMA over data through bar i),
so no lookahead.
"""

import pandas as pd

from strategies.base import adx as wilder_adx

DMI_PERIOD = 14

INDICATOR_COLS = [
    "adx",
    "plus_di",
    "minus_di",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dmi = wilder_adx(df["h"], df["l"], df["c"], DMI_PERIOD)
    df["adx"] = dmi["adx"]
    df["plus_di"] = dmi["plus_di"]
    df["minus_di"] = dmi["minus_di"]
    return df
