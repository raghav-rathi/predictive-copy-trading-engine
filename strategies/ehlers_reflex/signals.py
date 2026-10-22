"""Reflex zero-cross signals.

The Reflex oscillator is self-normalized around zero: positive means
the detrended trend sum points up, negative means it points down.
Entries ride the zero-cross itself — the zero-lag property means a
cross is already the confirmed turn, so there is no need to wait for
an overbought/oversold extreme:

    long_entry  = crossed_above(reflex, 0)
    short_entry = crossed_below(reflex, 0)

Exits are the opposite zero-cross: once a position is open, Reflex
changing sign means the trend leg failed, so get out even if the
stop/trail has not fired.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def _crossed_up_zero(s: pd.Series) -> pd.Series:
    """Zero cross up: s > 0 while the previous bar was <= 0."""
    return ((s > 0) & (s.shift(1) <= 0)).fillna(False)


def _crossed_down_zero(s: pd.Series) -> pd.Series:
    """Zero cross down: s < 0 while the previous bar was >= 0."""
    return ((s < 0) & (s.shift(1) >= 0)).fillna(False)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rx = df["reflex"]
    cross_up = _crossed_up_zero(rx)
    cross_dn = _crossed_down_zero(rx)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
