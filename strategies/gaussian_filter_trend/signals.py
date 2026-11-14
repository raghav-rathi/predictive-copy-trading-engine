"""Gaussian filter trend signals.

CORRECTED crossover direction (see indicators.py / CALIBRATION.md):
with Ehlers' alpha formula the period-30 filter is the FASTER tracker
and the period-10 filter the SLOWER baseline, so:

    long_entry  = period-30 filter crosses above period-10 filter
    short_entry = period-30 filter crosses below period-10 filter
    long_exit   = period-30 filter crosses below period-10 filter
    short_exit  = period-30 filter crosses above period-10 filter

On a sine wave the period-30 line crosses above the period-10 line
at price bottoms and below it at price tops, so this is a genuine
trend-following crossover (buy the turn up, sell the turn down).
The brief's literal direction (period-10 above period-30 = long)
was verified to fire at tops and is NOT shipped.

A plain two-line crossover on a smoother-than-EMA pair: the Gaussian
cascade rejects high-frequency chop better than an EMA pair of the
same periods, so crosses mark confirmed regime turns rather than
one-bar noise. Exits are the opposite cross -- the trend has turned,
not merely weakened.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = df["gf_p30"]  # measured fast tracker (period 30)
    slow = df["gf_p10"]  # measured slow baseline (period 10)
    cross_up = crossed_above(fast, slow).fillna(False)
    cross_dn = crossed_below(fast, slow).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_dn.astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
