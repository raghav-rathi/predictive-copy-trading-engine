"""VQI signals.

    long_entry  = VQI_t > VQI_{t-10} (rising "good" volatility) and
                  the |10-bar VQI change| clears 0.5x its 50-bar
                  median (the no-trade gate)
    short_entry = VQI_t < VQI_{t-10} and the gate clears

Exits: the 10-bar VQI change flips sign against the position, or the
20-bar EMA of close crosses against the position.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    chg = df["vqi_chg10"]
    gate = df["vqi_gate"].fillna(False)
    close = df["c"]
    ema20 = df["ema20"]
    df["long_entry"] = ((chg > 0) & gate).fillna(False).astype(bool)
    df["short_entry"] = ((chg < 0) & gate).fillna(False).astype(bool)
    df["long_exit"] = ((chg < 0) | crossed_below(close, ema20)).fillna(False).astype(bool)
    df["short_exit"] = ((chg > 0) | crossed_above(close, ema20)).fillna(False).astype(bool)
    return df
