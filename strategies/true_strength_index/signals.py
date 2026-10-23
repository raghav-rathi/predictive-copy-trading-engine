"""TSI signal-line cross system with a zero-territory filter.

Blau's canonical usage is a trend-following cross system on the TSI /
signal line. This module adds a momentum-regime filter so only crosses
that agree with the current territory are taken:

    long_entry  = TSI crosses above signal AND TSI > 0
    short_entry = TSI crosses below signal AND TSI < 0
    long_exit   = TSI crosses below signal
    short_exit  = TSI crosses above signal

Rationale: a signal-line cross while the oscillator is in negative
territory is a counter-trend / mean-reversion wobble far more often
than a genuine regime flip; the zero filter keeps the strategy in the
direction of the prevailing momentum regime. Exits are the raw
opposite cross (no territory filter) so a position is not held through
a confirmed momentum reversal.

Crosses use strategies.base.crossed_above/crossed_below on the raw
indicator columns: the signal on bar i uses data through bar i's close
only; the backtest harness executes at the i+1 open. All signal
columns are boolean with no NaN (warmup NaN comparisons fill False).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    tsi = df["tsi"]
    sig = df["tsi_signal"]
    cross_up = crossed_above(tsi, sig).fillna(False)
    cross_dn = crossed_below(tsi, sig).fillna(False)
    bull_territory = (tsi > 0).fillna(False)
    bear_territory = (tsi < 0).fillna(False)
    df["long_entry"] = (cross_up & bull_territory).astype(bool)
    df["short_entry"] = (cross_dn & bear_territory).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
