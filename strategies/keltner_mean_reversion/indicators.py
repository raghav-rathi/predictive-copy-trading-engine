"""Keltner channel indicators (mean-reversion fade).

Uses the house ``base.keltner``: EMA(20) midline with ATR(10)
bands at k=2.0 -- kc_mid / kc_upper / kc_lower. ATR(14) is
also computed for the risk layer (the harness sizes stops
off its own ATR(14); the column is kept here for inspection).

Columns:
    kc_mid, kc_upper, kc_lower, atr14

No lookahead: EMA and Wilder ATR are causal recursions.
"""

import pandas as pd

from strategies import base as B

EMA_N = 20
ATR_N = 10
K_MULT = 2.0


def add_indicators(
    df: pd.DataFrame,
    ema_n: int = EMA_N,
    atr_n: int = ATR_N,
    k: float = K_MULT,
) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"], ema_n=ema_n, atr_n=atr_n, k=k)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
