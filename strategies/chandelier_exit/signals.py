"""Chandelier Exit signals.

Entries (breakout): long when the close crosses above the prior 22-bar
high (prev close <= prev HH22 and close > HH22); short mirrors against
the prior 22-bar low. Exits (the chandelier itself): a long exits when
the close prints below chand_long; a short exits when the close prints
above chand_short. Signals are boolean-clean; execution happens at the
next bar's open per the base convention.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["hh22"]
    ll = df["ll22"]
    c = df["c"]
    prev_c = c.shift(1)
    prev_hh = hh.shift(1)
    prev_ll = ll.shift(1)

    long_entry = (prev_c <= prev_hh) & (c > hh)
    short_entry = (prev_c >= prev_ll) & (c < ll)

    long_exit = c < df["chand_long"]
    short_exit = c > df["chand_short"]

    df["long_entry"] = long_entry.fillna(False)
    df["short_entry"] = short_entry.fillna(False)
    df["long_exit"] = long_exit.fillna(False)
    df["short_exit"] = short_exit.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
