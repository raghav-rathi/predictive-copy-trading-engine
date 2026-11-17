"""EMA(20)/EMA(50) crossover with ADX(14) filter indicators.

Long: EMA(20) crosses above EMA(50) AND ADX > 25 AND +DI > -DI.
Short: EMA(20) crosses below EMA(50) AND ADX > 25 AND -DI > +DI.

ADX / +DI / -DI use the standard Wilder smoothing from
strategies.base.adx (no TA-Lib). EMA via strategies.base.ema.

Columns:
    ema20, ema50  -- exponential moving averages of close
    adx           -- Wilder ADX(14)
    plus_di       -- Wilder +DI(14)
    minus_di      -- Wilder -DI(14)
    atr           -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

EMA_FAST = 20
EMA_SLOW = 50
ADX_N = 14
ADX_ENTRY = 25
ADX_EXIT = 20

INDICATOR_COLS = ["ema20", "ema50", "adx", "plus_di", "minus_di", "atr"]


def add_indicators(df: pd.DataFrame, fast: int = EMA_FAST,
                   slow: int = EMA_SLOW, adx_n: int = ADX_N) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = B.ema(df["c"], fast)
    df["ema50"] = B.ema(df["c"], slow)
    d = B.adx(df["h"], df["l"], df["c"], adx_n)
    df["adx"] = d["adx"]
    df["plus_di"] = d["plus_di"]
    df["minus_di"] = d["minus_di"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
