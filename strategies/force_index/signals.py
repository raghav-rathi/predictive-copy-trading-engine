"""Force Index signals (Elder, Trading for a Living).

Trade in the direction of the 13-period EMA of Force Index (the trend):
  LONG  when FI13 > 0 and FI2 crosses back below 0  (pullback dip into force)
  SHORT when FI13 < 0 and FI2 crosses back above 0  (pullback pop into force)
Both EMAs on the same side of zero = no signal (trend entry already crowded).

Exits: FI13 flips sign (trend lost), or FI2 hooks back against the position:
a 1-bar peak of FI2 above zero while long (take the rally), a 1-bar trough
of FI2 below zero while short. Execution at the next bar's open per the
harness convention.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    uptrend = df["fi13"] > 0
    downtrend = df["fi13"] < 0
    zero = pd.Series(0.0, index=df.index)

    fi2_dip = B.crossed_below(df["fi2"], zero)   # pullback: fast force dives under zero
    fi2_pop = B.crossed_above(df["fi2"], zero)   # pullback: fast force pops over zero

    df["long_entry"] = uptrend & fi2_dip
    df["short_entry"] = downtrend & fi2_pop

    # FI2 hook against the position: 1-bar peak above zero while long,
    # 1-bar trough below zero while short (Elder's profit-taking hook).
    hook_dn = (df["fi2_prev"] > 0) & (df["fi2"] < df["fi2_prev"]) & (
        df["fi2_prev"] >= df["fi2"].shift(2)
    )
    hook_up = (df["fi2_prev"] < 0) & (df["fi2"] > df["fi2_prev"]) & (
        df["fi2_prev"] <= df["fi2"].shift(2)
    )

    df["long_exit"] = B.crossed_below(df["fi13"], zero) | hook_dn
    df["short_exit"] = B.crossed_above(df["fi13"], zero) | hook_up

    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
