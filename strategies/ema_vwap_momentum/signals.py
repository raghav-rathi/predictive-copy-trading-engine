"""EMA cross + session VWAP momentum signals.

Long entry:  EMA(9) crosses above EMA(21) while the close is above
             the session VWAP.
Short entry: EMA(9) crosses below EMA(21) while the close is below
             the session VWAP.
Long exit:   EMA cross against OR the close crosses back below the
             session VWAP.
Short exit:  EMA cross against OR the close crosses back above the
             session VWAP.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["ema_fast"], df["ema_slow"])
    cross_down = B.crossed_below(df["ema_fast"], df["ema_slow"])
    above_vwap = df["c"] > df["vwap_day"]
    below_vwap = df["c"] < df["vwap_day"]
    df["long_entry"] = (cross_up & above_vwap).fillna(False).astype(bool)
    df["short_entry"] = (cross_down & below_vwap).fillna(False).astype(bool)
    df["long_exit"] = (cross_down | below_vwap).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | above_vwap).fillna(False).astype(bool)
    return df
