"""2-bar key reversal pattern primitives (Larry Williams).

Per-bar pattern facts (no lookahead; each column on bar j uses
data through bar j's close only):

    down_bar    -- close < open (a down bar)
    up_bar      -- close > open (an up bar)
    lower_low   -- low[j] < low[j-1] (bar makes a new low vs prior bar)
    higher_high -- high[j] > high[j-1] (bar makes a new high vs prior bar)

The signal logic in signals.py combines these with one-bar shifts:
a bullish key reversal is a down bar making a lower low (bar i-1)
confirmed by the next bar closing above bar i-1's high (or close,
or with no confirmation — see signals.CONFIRM).
"""

import pandas as pd

from strategies import base as B  # noqa: F401  (kept for parity with other engines)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["down_bar"] = df["c"] < df["o"]
    df["up_bar"] = df["c"] > df["o"]
    df["lower_low"] = df["l"] < df["l"].shift(1)
    df["higher_high"] = df["h"] > df["h"].shift(1)
    return df
