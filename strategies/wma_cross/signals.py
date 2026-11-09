"""WMA crossover signals.

Long: WMA(9) crosses above WMA(21). Short: WMA(9) crosses below
WMA(21). Exit a long on the cross down; exit a short on the cross
up. All inputs are computed from data through bar i's close, so
signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["wma_fast"], df["wma_slow"])
    cross_down = crossed_below(df["wma_fast"], df["wma_slow"])
    df["long_entry"] = cross_up.fillna(False).astype(bool)
    df["short_entry"] = cross_down.fillna(False).astype(bool)
    df["long_exit"] = cross_down.fillna(False).astype(bool)
    df["short_exit"] = cross_up.fillna(False).astype(bool)
    return df
