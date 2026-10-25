"""SMA(20)/SMA(50) crossover — the slower, smoother sibling of ema_cross.

Same bare-crossover logic, slower averages: fewer signals, later
confirmation, less whipsaw in principle. Long on the 20-over-50 cross,
short on the cross under, exit on the opposite cross.

Columns:
    sma_fast, sma_slow -- simple moving averages of close
    atr                -- Wilder ATR(14) for the risk layer

No lookahead: SMAs are trailing windows.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 20
SLOW = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["sma_fast"] = B.sma(df["c"], FAST)
    df["sma_slow"] = B.sma(df["c"], SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
