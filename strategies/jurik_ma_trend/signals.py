"""Jurik MA trend signals.

Long: close crosses above the JMA and the JMA is rising (above its
previous bar). Short: close crosses below the JMA and the JMA is
falling. Exit a long on a cross back below the JMA; exit a short on
a cross back above the JMA. All inputs use only data through bar i's
close, so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["c"]
    jma = df["jma"]
    rising = df["jma_rising"].fillna(False)
    falling = (df["jma"] < df["jma"].shift(1)).fillna(False)
    df["long_entry"] = (crossed_above(close, jma) & rising).fillna(False).astype(bool)
    df["short_entry"] = (crossed_below(close, jma) & falling).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(close, jma).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(close, jma).fillna(False).astype(bool)
    return df
