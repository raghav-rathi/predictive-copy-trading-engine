"""ATR trailing-stop signals (Chandelier Exit family, Chuck LeBeau).

Long entry:  the regime flips long — the close crosses above the
             trailing stop from below (chand_dir -1 -> +1).
Short entry: the regime flips short — the close crosses below the
             trailing stop from above (chand_dir +1 -> -1).
Long exit:   the regime flips short (same bar as a short entry).
Short exit:  the regime flips long (same bar as a long entry).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies; the
regime flip is the system-defined exit, and the harness stop/trail
usually fires first inside a regime.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    direction = df["chand_dir"]
    long_entry = B.crossed_above(direction, 0.0)
    short_entry = B.crossed_below(direction, 0.0)
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = short_entry.fillna(False).astype(bool)
    df["short_exit"] = long_entry.fillna(False).astype(bool)
    return df
