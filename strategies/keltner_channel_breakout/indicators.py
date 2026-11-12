"""Keltner Channel Breakout indicators (Chester Keltner, 1960).

Mid line = EMA(20) of close. Bands = mid +/- 2.0 * ATR(10) (Wilder
ATR, shared strategies.base.atr primitive, alpha = 1/10). This is the
Linda Raschke ATR-based form of Keltner's channel: the EMA sets the
trend direction and the ATR sets the channel width.

Columns:

    kc_mid    -- EMA(20) of close
    kc_upper  -- kc_mid + 2.0 * ATR(10)
    kc_lower  -- kc_mid - 2.0 * ATR(10)
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: EMA(20) and ATR(10) on bar i use data through bar i's
close only.
"""

import pandas as pd

from strategies import base as B

EMA_N = 20
ATR_N = 10
MULT = 2.0

INDICATOR_COLS = ["kc_mid", "kc_upper", "kc_lower", "atr"]


def add_indicators(df: pd.DataFrame, ema_n: int = EMA_N,
                   atr_n: int = ATR_N, mult: float = MULT) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"],
                   ema_n=ema_n, atr_n=atr_n, k=mult)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
