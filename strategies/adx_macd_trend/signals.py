"""ADX + MACD trend signals.

Long entry: MACD line crosses above its signal line while ADX > 25
and +DI > -DI. Short entry: mirror (cross below, ADX > 25, -DI > +DI).

Exits: the opposite MACD cross, or ADX crossing below 20 (trend
strength has collapsed, so the trend thesis is dead even without a
momentum cross). Exits are stateless level/cross conditions; the
harness only acts on them while a position is open, so a persistent
ADX < 20 flag while flat is harmless. Boolean columns, no NaN,
no lookahead: every condition reads bars <= i, and the harness
executes at bar i+1's open.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ADX_ENTRY = 25.0
ADX_EXIT = 20.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    adx = df["adx"]
    plus_di = df["plus_di"]
    minus_di = df["minus_di"]
    macd = df["macd"]
    sig = df["macd_signal"]

    macd_up = B.crossed_above(macd, sig).fillna(False)
    macd_dn = B.crossed_below(macd, sig).fillna(False)
    adx_faded = B.crossed_below(adx, ADX_EXIT).fillna(False)
    strong = (adx > ADX_ENTRY).fillna(False)

    le = (macd_up & strong & (plus_di > minus_di)).fillna(False)
    se = (macd_dn & strong & (minus_di > plus_di)).fillna(False)
    lx = (macd_dn | adx_faded).fillna(False)
    sx = (macd_up | adx_faded).fillna(False)

    df["long_entry"] = np.asarray(le, dtype=bool)
    df["short_entry"] = np.asarray(se, dtype=bool)
    df["long_exit"] = np.asarray(lx, dtype=bool)
    df["short_exit"] = np.asarray(sx, dtype=bool)
    return df
