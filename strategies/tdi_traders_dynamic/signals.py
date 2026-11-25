"""Traders Dynamic Index signals (Dean Malone).

Long when the price line crosses above the signal line AND
the price line is above the base line AND the base line is
above 50; short when the price line crosses below the signal
line AND the price line is below the base line AND the base
line is below 50. Exit on the opposite price/signal cross.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["tdi_price"], df["tdi_signal"]).fillna(False)
    cross_down = crossed_below(df["tdi_price"], df["tdi_signal"]).fillna(False)
    long_entry = (
        cross_up & (df["tdi_price"] > df["tdi_base"]) & (df["tdi_base"] > 50)
    ).fillna(False)
    short_entry = (
        cross_down & (df["tdi_price"] < df["tdi_base"]) & (df["tdi_base"] < 50)
    ).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
