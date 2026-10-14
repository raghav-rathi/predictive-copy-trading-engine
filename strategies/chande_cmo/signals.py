"""CMO signals (extreme-level cross system).

long_entry  = CMO crosses above -50 (leaving oversold)
short_entry = CMO crosses below +50 (leaving overbought)
long_exit   = CMO crosses back below 0 (momentum fades)
short_exit  = CMO crosses back above 0 (momentum fades)
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cmo = df["cmo"]
    df["long_entry"] = B.crossed_above(cmo, -50.0)
    df["short_entry"] = B.crossed_below(cmo, 50.0)
    df["long_exit"] = B.crossed_below(cmo, 0.0)
    df["short_exit"] = B.crossed_above(cmo, 0.0)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
