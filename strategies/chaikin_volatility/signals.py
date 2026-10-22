"""Chaikin Volatility threshold-cross signals with an SMA50 trend filter.

Chaikin Volatility is direction-agnostic: a spike means the average
trading range is *expanding*, whatever the price direction. This engine
treats a cross above +trigger as "volatility expansion is starting"
and takes the position *with* the prevailing trend (SMA50) rather than
against it:

    long_entry  = crossed_above(cv, +trigger) & (close > sma50)
    short_entry = crossed_above(cv, +trigger) & (close < sma50)

Because range expansion often marks climactic participation, exits are
taken when the expansion rolls over — cv crosses back below the
trigger, or below zero (range contracting outright):

    long_exit   = crossed_below(cv, trigger) | crossed_below(cv, 0)
    short_exit  = crossed_below(cv, trigger) | crossed_below(cv, 0)

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

TRIGGER = 5.0  # shipped default, fixed a priori (see CALIBRATION.md)


def _const_like(series: pd.Series, value: float) -> pd.Series:
    return pd.Series(value, index=series.index)


def add_signals(df: pd.DataFrame, trigger: float = TRIGGER) -> pd.DataFrame:
    df = df.copy()
    cv = df["cv"]
    up = crossed_above(cv, _const_like(cv, trigger)).fillna(False)
    dn_trig = crossed_below(cv, _const_like(cv, trigger)).fillna(False)
    dn_zero = crossed_below(cv, _const_like(cv, 0.0)).fillna(False)
    above = (df["c"] > df["sma50"]).fillna(False)
    below = (df["c"] < df["sma50"]).fillna(False)
    df["long_entry"] = (up & above).astype(bool)
    df["short_entry"] = (up & below).astype(bool)
    df["long_exit"] = (dn_trig | dn_zero).astype(bool)
    df["short_exit"] = (dn_trig | dn_zero).astype(bool)
    return df
