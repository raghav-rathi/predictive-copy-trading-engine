"""Rob Carver EWMAC signals (Systematic Trading).

Long when the combined forecast crosses above +10, short when it
crosses below -10; flat between (longs exit when the forecast falls
back below +10, shorts exit when it rises back above -10). The
forecast-band exit does the trade management, so risk.py carries no
trailing and no fixed target.
"""

import pandas as pd

from strategies.carver_ewmac import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    f = df["forecast"]
    prev = f.shift(1)
    df["long_entry"] = ((prev <= I.LONG_THRESHOLD) & (f > I.LONG_THRESHOLD)).fillna(False)
    df["short_entry"] = ((prev >= I.SHORT_THRESHOLD) & (f < I.SHORT_THRESHOLD)).fillna(False)
    df["long_exit"] = (f < I.LONG_THRESHOLD).fillna(False)
    df["short_exit"] = (f > I.SHORT_THRESHOLD).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
