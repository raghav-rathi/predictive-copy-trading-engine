"""Ehlers Roofing Filter signals: the roofing line IS the signal.

The high-pass stage detrends price, so the roofing line oscillates
around zero and its zero crossings are cycle turns:

    long_entry  = roofing crosses above 0
    short_entry = roofing crosses below 0
    long_exit   = roofing crosses below 0  (opposite zero cross)
    short_exit  = roofing crosses above 0  (opposite zero cross)

No extra filters: the filter itself is the trend/cycle estimator, and
adding a slope or threshold gate would re-introduce the lag the
Roofing Filter exists to remove. All conditions read bar-j closes at
bar j; the harness executes at the next bar's open. Signal columns
are boolean, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    roof = df["roofing"]
    xup = crossed_above(roof, 0).fillna(False)
    xdn = crossed_below(roof, 0).fillna(False)
    df["long_entry"] = xup.astype(bool)
    df["short_entry"] = xdn.astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
