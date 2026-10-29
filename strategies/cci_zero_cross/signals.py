"""CCI zero-line trend-cross signals.

Long entry: CCI crosses UP through zero while price is above
its SMA(50) — the oscillator's regime flip agrees with the price
trend, so the cross is a with-trend continuation signal, not a
counter-trend guess.

Short entry: mirror — CCI crosses DOWN through zero while price
is below its SMA(50).

Exits: the opposite zero cross (a long that sees CCI cross back
below zero has lost its regime; a short mirrors). No level
filter on exits — once the trade is on, the zero line is the
whole thesis.

This is deliberately different from cci_extreme (which trades
the +/-100 return) and cci_divergence (which trades pivot
disagreement): here the zero line plus the trend filter are the
entire signal, and a cross against the trend is ignored.

All conditions read bar-i closes; the harness executes at bar
i+1's open. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cci = df["cci"]
    above = df["c"] > df["trend_sma"]
    below = df["c"] < df["trend_sma"]

    df["long_entry"] = (crossed_above(cci, 0) & above).fillna(False).astype(bool)
    df["short_entry"] = (crossed_below(cci, 0) & below).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(cci, 0).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(cci, 0).fillna(False).astype(bool)
    return df
