"""Larry Williams %R indicators.

%R = (highest high - close) / (highest high - lowest low) * -100,
ranging from -100 (close at the low) to 0 (close at the high).
Also tracks bars since the last -100 extreme and the last 0 extreme —
the trigger needs at least ``wait`` bars between the extreme and the
reversal signal.
"""

import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame, n: int = 14, wait: int = 5) -> pd.DataFrame:
    df = df.copy()
    h, l, c = df["h"], df["l"], df["c"]
    hh = h.rolling(n, min_periods=n).max()
    ll = l.rolling(n, min_periods=n).min()
    denom = (hh - ll).replace(0, np.nan)
    df["pct_r"] = (((hh - c) / denom) * -100).fillna(-50.0)

    idx = np.arange(len(df))
    last_low = pd.Series(
        np.where(df["pct_r"] == -100.0, idx, np.nan), index=df.index
    ).ffill()
    last_high = pd.Series(
        np.where(df["pct_r"] == 0.0, idx, np.nan), index=df.index
    ).ffill()
    df["since_low_extreme"] = idx - last_low
    df["since_high_extreme"] = idx - last_high
    return df
