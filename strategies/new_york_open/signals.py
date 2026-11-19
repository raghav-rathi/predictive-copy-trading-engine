"""New York open momentum signals.

Long entry:  close above the first-hour (13:00 UTC bar) high during
             the 14:00-17:00 UTC window — long_trigger.
Short entry: close below the first-hour low during the window —
             short_trigger.
Long exit:   the 21:00 UTC bar close (time exit) OR an opposite
             short break.
Short exit:  the 21:00 UTC bar close (time exit) OR an opposite
             long break.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
max hold 48 bars. Signal columns are boolean, no NaN, no lookahead
(the harness executes at the next bar's open, so the 21:00-bar time
exit fills at the 22:00 open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = df["long_trigger"].fillna(False).astype(bool)
    short_trig = df["short_trigger"].fillna(False).astype(bool)
    time_exit = df["ny_time_exit"].fillna(False).astype(bool)
    df["long_entry"] = long_trig
    df["short_entry"] = short_trig
    df["long_exit"] = (time_exit | short_trig).fillna(False).astype(bool)
    df["short_exit"] = (time_exit | long_trig).fillna(False).astype(bool)
    return df
