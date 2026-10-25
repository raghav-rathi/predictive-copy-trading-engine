"""EMA(9)/EMA(21) crossover — the textbook moving-average trend signal.

Long when the fast EMA crosses above the slow EMA, short on the cross
below; exits on the opposite cross. No other filter: this is the bare
crossover, shipped so the backtest measures exactly what the classic
signal is worth on 1h crypto (fees included), not a filtered variant.

Columns:
    ema_fast, ema_slow -- exponential moving averages of close
    atr                -- Wilder ATR(14) for the risk layer

No lookahead: EMAs are causal (ewm, adjust=False).
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 9
SLOW = 21


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = B.ema(df["c"], FAST)
    df["ema_slow"] = B.ema(df["c"], SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
