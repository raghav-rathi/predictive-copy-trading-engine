"""CMF signals (zero-cross + price-regime filter).

long_entry  = CMF crosses above 0 while close > 200-bar SMA
short_entry = CMF crosses below 0 while close < 200-bar SMA
long_exit   = CMF crosses back below 0
short_exit  = CMF crosses back above 0
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cmf, reg = df["cmf"], df["cmf_regime"]
    c = df["c"]
    df["long_entry"] = B.crossed_above(cmf, 0.0) & (c > reg)
    df["short_entry"] = B.crossed_below(cmf, 0.0) & (c < reg)
    df["long_exit"] = B.crossed_below(cmf, 0.0)
    df["short_exit"] = B.crossed_above(cmf, 0.0)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
