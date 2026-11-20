"""EMA cross + session VWAP momentum indicators.

EMA(9)/EMA(21) from strategies.base and session VWAP anchored to
each UTC day (reset 00:00 UTC; VWAP = cumulative sum(tp * v) /
sum(v), tp = (h + l + c) / 3) via strategies.base.anchored_vwap.

Columns:
    ema_fast / ema_slow -- EMA(9) / EMA(21) of close
    vwap_day -- session VWAP (defined from bar 0 of each UTC day)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
The VWAP resets at the UTC-day boundary using only bars of the
current day.
"""

import pandas as pd

from strategies import base as B

EMA_FAST = 9
EMA_SLOW = 21

INDICATOR_COLS = ["ema_fast", "ema_slow", "vwap_day", "atr"]


def add_indicators(df: pd.DataFrame, fast: int = EMA_FAST,
                   slow: int = EMA_SLOW) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = B.ema(df["c"], fast)
    df["ema_slow"] = B.ema(df["c"], slow)
    df["vwap_day"] = B.anchored_vwap(df["h"], df["l"], df["c"],
                                     df["v"], df["t"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
