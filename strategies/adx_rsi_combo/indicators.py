"""ADX + RSI combo indicators.

ADX(14) (Wilder) as the trend-strength filter and RSI(14) (Wilder) as
the momentum trigger:

    adx    -- Wilder ADX(14), 0-100; > 25 = a trend worth trading
    plus_di, minus_di -- Wilder directional indicators (exposed for
                        inspection; the entry rule does not use them)
    rsi    -- Wilder RSI(14)
    atr    -- Wilder ATR(14) for the risk layer

No lookahead: every column on bar i uses only data through bar i's
close.
"""

import pandas as pd

from strategies import base as B

ADX_N = 14
RSI_N = 14

INDICATOR_COLS = ["adx", "plus_di", "minus_di", "rsi", "atr"]


def add_indicators(df: pd.DataFrame, adx_n: int = ADX_N,
                   rsi_n: int = RSI_N) -> pd.DataFrame:
    df = df.copy()
    di = B.adx(df["h"], df["l"], df["c"], adx_n)
    df["adx"] = di["adx"]
    df["plus_di"] = di["plus_di"]
    df["minus_di"] = di["minus_di"]
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
