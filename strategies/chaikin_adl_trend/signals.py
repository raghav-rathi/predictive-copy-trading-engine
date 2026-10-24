"""Chaikin ADL trend signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(adl, adl_sma) & (close > sma50)
    short_entry = crossed_below(adl, adl_sma) & (close < sma50)

The ADL cross is the money-flow trigger: the ADL crossing above its
10-bar average means accumulation is accelerating (buyers lifting
closes toward the highs on volume); crossing below means
distribution is accelerating. A bare ADL cross is noise in chop,
so the 50-bar SMA filter demands the cross agree with the
medium-term trend — no buying an ADL up-cross while price sits
below its 50-bar average, and no shorting a down-cross while
price sits above it.

Exits are the pure opposite ADL crosses (no trend filter — once
the trade is on, the exit should be trigger-happy, not gated):

    long_exit  = crossed_below(adl, adl_sma)
    short_exit = crossed_above(adl, adl_sma)

All conditions read bar-j closes at bar j; the harness executes at
the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    adl = df["adl"]
    adl_sma = df["adl_sma"]
    sma50 = df["sma50"]
    c = df["c"]

    xup = crossed_above(adl, adl_sma).fillna(False)
    xdn = crossed_below(adl, adl_sma).fillna(False)
    above = (c > sma50).fillna(False)
    below = (c < sma50).fillna(False)

    df["long_entry"] = (xup & above).astype(bool)
    df["short_entry"] = (xdn & below).astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
