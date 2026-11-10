"""Chande Dynamic Momentum Index signals.

Chande recommends using the DMI "much the same as the RSI", so the
signal rules are the classic RSI overbought/oversold cross rules
applied to the DMI:

  Long entry:  DMI crosses up through 30.
  Short entry: DMI crosses down through 70.
  Long exit:   DMI crosses above 70 (overbought).
  Short exit:  DMI crosses below 30 (oversold).

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. Crosses use the previous bar's DMI, so a
NaN DMI on either bar produces no signal.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

OVERSOLD = 30.0
OVERBOUGHT = 70.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dmi = df["dmi"]
    cross_up_30 = crossed_above(dmi, OVERSOLD)
    cross_down_70 = crossed_below(dmi, OVERBOUGHT)
    cross_up_70 = crossed_above(dmi, OVERBOUGHT)
    cross_down_30 = crossed_below(dmi, OVERSOLD)
    df["long_entry"] = cross_up_30.fillna(False).astype(bool)
    df["short_entry"] = cross_down_70.fillna(False).astype(bool)
    df["long_exit"] = cross_up_70.fillna(False).astype(bool)
    df["short_exit"] = cross_down_30.fillna(False).astype(bool)
    return df
