"""Larry Williams %R signals — the published reversal trigger.

Long: %R touches -100; at least ``wait`` bars pass; then %R rises above
-85 -> long_entry. Short mirror: %R touches 0, ``wait`` bars pass, then
%R falls below -15 -> short_entry. Exits when %R reaches the opposite
extreme zone: long_exit above -20, short_exit below -80.
"""

import pandas as pd

from strategies import base as B


def add_signals(
    df: pd.DataFrame,
    wait: int = 5,
    long_trigger: float = -85.0,
    short_trigger: float = -15.0,
    long_exit_level: float = -20.0,
    short_exit_level: float = -80.0,
) -> pd.DataFrame:
    df = df.copy()
    pct = df["pct_r"]

    df["long_entry"] = (
        (df["since_low_extreme"] >= wait) & B.crossed_above(pct, long_trigger)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (df["since_high_extreme"] >= wait) & B.crossed_below(pct, short_trigger)
    ).fillna(False).astype(bool)
    df["long_exit"] = (pct > long_exit_level).fillna(False).astype(bool)
    df["short_exit"] = (pct < short_exit_level).fillna(False).astype(bool)
    return df
