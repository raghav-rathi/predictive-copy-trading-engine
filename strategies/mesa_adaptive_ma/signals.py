"""MESA Adaptive Moving Average crossover signals.

Long: MAMA crosses above FAMA. Short: MAMA crosses below FAMA.
Exit a long on MAMA crossing below FAMA; exit a short on MAMA
crossing above FAMA. All inputs are computed from data through bar
i's close, so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["mama"], df["fama"])
    cross_down = crossed_below(df["mama"], df["fama"])
    df["long_entry"] = cross_up.fillna(False).astype(bool)
    df["short_entry"] = cross_down.fillna(False).astype(bool)
    df["long_exit"] = cross_down.fillna(False).astype(bool)
    df["short_exit"] = cross_up.fillna(False).astype(bool)
    return df
