"""Range Action Verification Index (Tushar Chande).

RAVI = 100 * (SMA(7) - SMA(65)) / SMA(65): the percentage gap
between a 7-bar and a 65-bar average. Chande's reference lines
are +/-0.3%: crossing the upper line starts an uptrend, crossing
the lower line starts a downtrend, and reverting to zero ends it.

Columns:
    ravi, atr
"""

import pandas as pd

from strategies import base as B

FAST = 7
SLOW = 65


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = B.sma(df["c"], FAST)
    slow = B.sma(df["c"], SLOW)
    df["ravi"] = 100.0 * (fast - slow) / slow
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
