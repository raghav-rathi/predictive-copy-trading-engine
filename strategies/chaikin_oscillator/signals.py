"""Chaikin Oscillator signals.

Long: CHO crosses above zero AND close above SMA(50). Short: CHO
crosses below zero AND close below SMA(50). Exit a long on a reverse
zero cross (CHO crosses below zero), a short on CHO crossing above
zero. Crosses use only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cho = df["co_cho"]
    sma50 = df["sma50"]
    cross_up = B.crossed_above(cho, 0.0).fillna(False)
    cross_dn = B.crossed_below(cho, 0.0).fillna(False)
    above_sma = (df["c"] > sma50).fillna(False)
    below_sma = (df["c"] < sma50).fillna(False)
    df["long_entry"] = (cross_up & above_sma).astype(bool)
    df["short_entry"] = (cross_dn & below_sma).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
