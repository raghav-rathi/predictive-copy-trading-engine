"""Price channel breakout signals.

Long entry:  close breaks above the 30-bar channel high.
Short entry: close breaks below the 30-bar channel low.
Long exit:   close crosses back below the channel midline.
Short exit:  close crosses back above the channel midline.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
midline cross; the midline cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = B.crossed_above(df["c"], df["channel_high"]).fillna(False)
    short_entry = B.crossed_below(df["c"], df["channel_low"]).fillna(False)
    long_exit = B.crossed_below(df["c"], df["channel_mid"]).fillna(False)
    short_exit = B.crossed_above(df["c"], df["channel_mid"]).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
