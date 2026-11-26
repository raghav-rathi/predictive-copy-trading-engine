"""Dynamic Momentum Index signals.

Long when DMI crosses up through 30; short when DMI crosses
down through 70; exit when DMI crosses back through 50
(long exit on a cross below 50, short exit on a cross above
50). Crosses use base.crossed_above / crossed_below, so each
entry is transition-only — a single bar — and the signal is
judged on bar i's close, executed at bar i+1's open by the
harness. No lookahead: DMI at bar i uses only closes through
bar i, and the cross compares bar i against bar i-1.

Signal columns are boolean, no NaN.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

LONG_LEVEL = 30.0
SHORT_LEVEL = 70.0
EXIT_LEVEL = 50.0


def add_signals(
    df: pd.DataFrame,
    long_level: float = LONG_LEVEL,
    short_level: float = SHORT_LEVEL,
    exit_level: float = EXIT_LEVEL,
) -> pd.DataFrame:
    df = df.copy()
    dmi = df["dmi"]
    df["long_entry"] = crossed_above(dmi, long_level).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(dmi, short_level).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(dmi, exit_level).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(dmi, exit_level).fillna(False).astype(bool)
    return df
