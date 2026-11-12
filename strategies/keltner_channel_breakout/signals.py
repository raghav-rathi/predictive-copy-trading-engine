"""Keltner Channel Breakout signals.

Long entry:  close > upper Keltner band (EMA(20) + 2.0 * ATR(10)).
Short entry: close < lower Keltner band (EMA(20) - 2.0 * ATR(10)).
Long exit:   close back inside the channel (close < upper band).
Short exit:  close back inside the channel (close > lower band).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
channel-re-entry exit; the re-entry exit is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_trig = (df["c"] > df["kc_upper"]).fillna(False)
    short_trig = (df["c"] < df["kc_lower"]).fillna(False)
    df["long_entry"] = long_trig.astype(bool)
    df["short_entry"] = short_trig.astype(bool)
    df["long_exit"] = (df["c"] < df["kc_upper"]).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > df["kc_lower"]).fillna(False).astype(bool)
    return df
