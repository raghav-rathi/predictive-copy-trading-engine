"""PGO signals (volatility-normalized momentum breakout).

long_entry  = PGO crosses above +1.0 (up-thrust beyond one ATR)
short_entry = PGO crosses below -1.0 (down-thrust beyond one ATR)
long_exit   = PGO crosses back below 0 (stretch faded)
short_exit  = PGO crosses back above 0 (stretch faded)
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B
from strategies.pgo import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pgo = df["pgo"]
    lv = I.ENTRY_LEVEL
    df["long_entry"] = B.crossed_above(pgo, lv)
    df["short_entry"] = B.crossed_below(pgo, -lv)
    df["long_exit"] = B.crossed_below(pgo, 0.0)
    df["short_exit"] = B.crossed_above(pgo, 0.0)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
