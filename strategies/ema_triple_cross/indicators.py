"""Triple-EMA alignment indicators (3/8/21).

A bar is bull-stacked when EMA(3) > EMA(8) > EMA(21) and
bear-stacked when the order reverses. Stacking is computed
from EMAs that use only closes through the current bar, so it
is causal. Columns: ema_fast, ema_mid, ema_slow, bull_stack,
bear_stack, atr.
"""

import pandas as pd

from strategies import base as B

FAST, MID, SLOW = 3, 8, 21


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_fast"] = B.ema(df["c"], FAST)
    df["ema_mid"] = B.ema(df["c"], MID)
    df["ema_slow"] = B.ema(df["c"], SLOW)
    df["bull_stack"] = (
        (df["ema_fast"] > df["ema_mid"]) & (df["ema_mid"] > df["ema_slow"])
    )
    df["bear_stack"] = (
        (df["ema_fast"] < df["ema_mid"]) & (df["ema_mid"] < df["ema_slow"])
    )
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
