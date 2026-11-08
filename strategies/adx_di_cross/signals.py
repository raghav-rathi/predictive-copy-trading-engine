"""Wilder DMI crossover signals.

Long: +DI crosses above -DI AND ADX > 25 AND ADX rising (ADX above its
previous bar) AND (+DI - -DI) >= 5 at the cross. Short: mirror (-DI
crosses above +DI, ADX > 25 and rising, (-DI - +DI) >= 5). Exit a long
on -DI crossing above +DI or ADX < 20; exit a short on +DI crossing
above -DI or ADX < 20. All inputs are computed from data through bar
i's close, so signals on bar i use no future data.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    plus_di = df["plus_di"]
    minus_di = df["minus_di"]
    adx = df["adx"]
    cross_up = (plus_di > minus_di) & (plus_di.shift(1) <= minus_di.shift(1))
    cross_down = (minus_di > plus_di) & (minus_di.shift(1) <= plus_di.shift(1))
    adx_rising = (adx > adx.shift(1)).fillna(False)
    adx_strong = (adx > 25).fillna(False)
    spread = plus_di - minus_di
    df["long_entry"] = (
        cross_up & adx_strong & adx_rising & (spread >= 5)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        cross_down & adx_strong & adx_rising & (spread <= -5)
    ).fillna(False).astype(bool)
    df["long_exit"] = (cross_down | (adx < 20)).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | (adx < 20)).fillna(False).astype(bool)
    return df
