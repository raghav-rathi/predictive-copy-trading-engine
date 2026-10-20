"""OU half-life z-score mean-reversion signals.

Long:  z < -2 AND the AR(1) half-life is valid (mean-reverting, 5-120
       bars). Exit when z >= 0 (deviation closed).
Short: z > 2 AND half-life valid. Exit when z <= 0.
No other exits — the risk config carries the hard stop (2.5xATR) and a
200-bar max hold.
"""

from __future__ import annotations

import pandas as pd

Z_ENTRY = 2.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    valid = df["hl_valid"].fillna(False).astype(bool)
    z = df["zscore"]
    long_in = ((z < -Z_ENTRY) & valid).fillna(False)
    short_in = ((z > Z_ENTRY) & valid).fillna(False)
    out["long_entry"] = long_in.astype(bool)
    out["short_entry"] = short_in.astype(bool)
    out["long_exit"] = (z >= 0.0).fillna(False).astype(bool)
    out["short_exit"] = (z <= 0.0).fillna(False).astype(bool)
    return out
