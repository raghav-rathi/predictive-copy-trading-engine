"""Tushar Chande's Aroon oscillator indicators (1995).

AroonUp(n)   = 100 * (n - bars since highest high in n bars) / n
AroonDown(n) = 100 * (n - bars since lowest low in n bars) / n
AroonOsc = AroonUp - AroonDown. Values near +100 mean a fresh high (new
uptrend); near -100 a fresh low. Classic n=25. All causal: only data
through bar i's close.
"""

import numpy as np
import pandas as pd

N = 25       # Chande's classic period
STRONG = 70  # fresh-trend threshold for entries


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    since_high = df["h"].rolling(N, min_periods=N).apply(
        lambda x: (N - 1) - np.argmax(x), raw=True
    )
    since_low = df["l"].rolling(N, min_periods=N).apply(
        lambda x: (N - 1) - np.argmin(x), raw=True
    )
    df["aroon_up"] = 100.0 * (N - since_high) / N
    df["aroon_down"] = 100.0 * (N - since_low) / N
    df["aroon_osc"] = df["aroon_up"] - df["aroon_down"]
    return df
