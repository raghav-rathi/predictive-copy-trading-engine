"""Early Onset Trend signals (Ehlers, TASC Aug 2014).

The published indicator has no separate trigger line: it plots two
quotient transforms of the same normalised roofing-filter output, and
Ehlers' own strategy code trades their zero crossings — buy when
Quotient1 crosses over 0, sell when Quotient2 crosses under 0. This
module maps the brief's "EOT crossing above/below its trigger" onto
that published form:

Long entry: Quotient1 (K=0.85) crosses above 0.
Short entry: Quotient2 (K=0.40) crosses below 0.
Long exit: Quotient2 crosses below 0 (the published sell signal).
Short exit: Quotient1 crosses above 0 (the published buy signal).

All inputs are computed from data through bar i's close, so signals
on bar i use no future data. The harness executes at bar i+1's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    q1_cross_up = crossed_above(df["q1"], 0.0).fillna(False)
    q2_cross_down = crossed_below(df["q2"], 0.0).fillna(False)
    df["long_entry"] = q1_cross_up.astype(bool)
    df["short_entry"] = q2_cross_down.astype(bool)
    df["long_exit"] = q2_cross_down.astype(bool)
    df["short_exit"] = q1_cross_up.astype(bool)
    return df
