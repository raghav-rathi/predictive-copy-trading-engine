"""Aroon(25) by Tushar Chande (1995).

    Aroon Up   = 100 * (25 - bars since 25-bar high) / 25
    Aroon Down = 100 * (25 - bars since 25-bar low) / 25

"Bars since" counts back from the current bar within the
25-bar window inclusive of the current bar, so a new high on
the current bar gives Aroon Up = 100, and a high 25 bars ago
(about to leave the window) gives 0. On a tied high/low the
most recent occurrence is used, matching the "since the most
recent high/low" definition. Values are NaN before 25 bars
(first valid at bar 24).

Columns:
    aroon_up   -- Aroon Up(25), 0-100
    aroon_down -- Aroon Down(25), 0-100
    atr        -- Wilder ATR(14) for the risk layer

Causal: each value uses only bars through the current close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PERIOD = 25


def _bars_since_extreme(values: np.ndarray, n: int, want_max: bool) -> np.ndarray:
    out = np.full(len(values), np.nan)
    for i in range(n - 1, len(values)):
        window = values[i - n + 1 : i + 1]
        # Reverse so argmax/argmin finds the MOST RECENT extreme.
        rev = window[::-1]
        idx = int(np.argmax(rev)) if want_max else int(np.argmin(rev))
        out[i] = idx  # bars since the most recent extreme
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    since_high = _bars_since_extreme(h, PERIOD, want_max=True)
    since_low = _bars_since_extreme(l, PERIOD, want_max=False)
    df["aroon_up"] = 100.0 * (PERIOD - since_high) / PERIOD
    df["aroon_down"] = 100.0 * (PERIOD - since_low) / PERIOD
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
