"""RSI(2) mean-reversion indicators: Larry Connors' RSI(2) system
(Short Term Trading Strategies That Work, 2008).

Trend filter: SMA(200) on 1h closes. Momentum: Wilder RSI(2).
Exit reference: SMA(5). All computed from closes only, using data
through bar i's close — no lookahead.
"""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["rsi2", "sma200", "sma5"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi2"] = B.rsi(df["c"], 2)
    df["sma200"] = B.sma(df["c"], 200)
    df["sma5"] = B.sma(df["c"], 5)
    return df
