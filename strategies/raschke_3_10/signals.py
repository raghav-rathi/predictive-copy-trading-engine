"""Raschke 3/10 signals (Raschke & Connors, "Street Smarts").

Long when the oscillator crosses above its signal line AND the
oscillator is positive (Raschke's trend filter — only take momentum
trades in the direction of the prevailing drift); short when it crosses
below the signal line AND the oscillator is negative.  Exit when the
oscillator crosses back through the signal line.  Risk-level exits
(1.5xATR stop, 48-bar max hold) come from risk.py.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    osc = df["osc_3_10"]
    sig = df["osc_3_10_signal"]
    cross_up = B.crossed_above(osc, sig).fillna(False)
    cross_dn = B.crossed_below(osc, sig).fillna(False)
    df["long_entry"] = (cross_up & (osc > 0)).fillna(False)
    df["short_entry"] = (cross_dn & (osc < 0)).fillna(False)
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
