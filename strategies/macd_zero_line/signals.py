"""MACD zero-line cross signals.

Long on the MACD line crossing above zero; short on crossing below
zero; exit on the reverse zero cross. Crosses are detected from the
current and previous bar's MACD line values only.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    line = df["macd_line"]
    df["long_entry"] = B.crossed_above(line, 0.0).fillna(False)
    df["short_entry"] = B.crossed_below(line, 0.0).fillna(False)
    df["long_exit"] = B.crossed_below(line, 0.0).fillna(False)
    df["short_exit"] = B.crossed_above(line, 0.0).fillna(False)
    return df
