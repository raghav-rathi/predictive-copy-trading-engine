"""Wilder Volatility System signals.

Long entry:  close > previous bar's high + ATR(7).
Short entry: close < previous bar's low - ATR(7).
Long exit:   the short trigger fires (close < previous bar's low
             - ATR(7)) -- the system reverses on the opposite trigger.
Short exit:  the long trigger fires.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
reverse trigger; the reverse trigger is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = (df["c"] > df["vol_long_trigger"]).fillna(False)
    short_trig = (df["c"] < df["vol_short_trigger"]).fillna(False)
    df["long_entry"] = long_trig.astype(bool)
    df["short_entry"] = short_trig.astype(bool)
    df["long_exit"] = short_trig.astype(bool)
    df["short_exit"] = long_trig.astype(bool)
    return df
