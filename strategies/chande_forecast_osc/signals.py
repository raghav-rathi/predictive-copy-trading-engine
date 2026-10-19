"""Chande Forecast Oscillator signals.

Long when FO crosses above its 3-bar signal line with FO > 0 (price
beating its own linear forecast while the oscillator turns up); short
when FO crosses below its signal line with FO < 0.

Exits are the cross back through the signal line: a long exits when FO
crosses back below the signal, a short exits when FO crosses back
above it.

All signal columns are boolean, no NaN; execution at next-bar open is
handled by the harness.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fo, sig = df["fo"], df["fo_signal"]
    cross_up = B.crossed_above(fo, sig).fillna(False)
    cross_dn = B.crossed_below(fo, sig).fillna(False)
    df["long_entry"] = (cross_up & (fo > 0)).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & (fo < 0)).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
