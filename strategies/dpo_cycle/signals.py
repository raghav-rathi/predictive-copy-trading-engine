"""DPO signals (cycle zero-cross system).

long_entry  = DPO crosses above 0 (cycle turns up)
short_entry = DPO crosses below 0 (cycle turns down)
long_exit   = DPO crosses back below 0
short_exit  = DPO crosses back above 0
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dpo = df["dpo"]
    long_x = B.crossed_above(dpo, 0.0)
    short_x = B.crossed_below(dpo, 0.0)
    df["long_entry"] = long_x
    df["short_entry"] = short_x
    df["long_exit"] = short_x
    df["short_exit"] = long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
