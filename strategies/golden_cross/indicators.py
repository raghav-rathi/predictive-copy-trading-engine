"""Golden Cross / Death Cross indicators (classic SMA cross).

    sma50  = SMA(close, 50)
    sma200 = SMA(close, 200)
    sma_diff = sma50 - sma200  (positive in a golden-cross regime)

The 50/200-day cross is the textbook long-term trend signal; on
1h bars the same construction is a ~2-day vs ~8-day trend filter.
The cross itself is slow by design — it confirms a regime change
rather than predicting one — which is why the holding window is
the longest of this batch.

Columns:

    sma50, sma200 -- simple moving averages of close
    sma_diff     -- sma50 minus sma200
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n).
"""

import pandas as pd

from strategies import base as B

FAST_N = 50        # shipped defaults (fixed a priori)
SLOW_N = 200


def add_indicators(df: pd.DataFrame, fast_n: int = FAST_N,
                   slow_n: int = SLOW_N) -> pd.DataFrame:
    df = df.copy()
    df["sma50"] = B.sma(df["c"], fast_n)
    df["sma200"] = B.sma(df["c"], slow_n)
    df["sma_diff"] = df["sma50"] - df["sma200"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
