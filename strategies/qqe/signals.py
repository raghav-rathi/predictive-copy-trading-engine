"""QQE signals — the documented Fast-TL / Slow-TL crossover:
  long_entry:  fast trailing level crosses above the slow trailing level
  short_entry: fast trailing level crosses below the slow trailing level
Exits: the opposite cross. The 50-level of the smoothed RSI is logged
as context (qqe_rsindex) but is not a trigger here.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast, slow = df["qqe_fast"], df["qqe_slow"]
    df["long_entry"] = B.crossed_above(fast, slow).fillna(False)
    df["short_entry"] = B.crossed_below(fast, slow).fillna(False)
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    return df
