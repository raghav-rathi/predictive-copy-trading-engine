"""Triple EMA Crossover indicators.

EMA(5), EMA(13), EMA(50) via strategies.base ema() (pandas ewm,
span=n, adjust=False). The fast EMA crossing the medium EMA is the
trigger; the slow EMA is the trend filter: a long needs the stack
EMA5 > EMA13 > EMA50, a short the stack EMA5 < EMA13 < EMA50.

Columns:
    ema_fast / ema_mid / ema_slow -- EMA(5) / EMA(13) / EMA(50)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every EMA value on bar i uses closes through bar i
only.
"""

import pandas as pd

from strategies import base as B

FAST_N = 5
MID_N = 13
SLOW_N = 50
ATR_N = 14


def add_indicators(df: pd.DataFrame, fast_n: int = FAST_N,
                   mid_n: int = MID_N, slow_n: int = SLOW_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["ema_fast"] = B.ema(c, fast_n)
    df["ema_mid"] = B.ema(c, mid_n)
    df["ema_slow"] = B.ema(c, slow_n)
    df["atr"] = B.atr(df["h"], df["l"], c, atr_n)
    return df
