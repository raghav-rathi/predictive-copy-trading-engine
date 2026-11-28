"""Parkinson realized-volatility indicators (Parkinson 1980).

    pk_var    -- per-bar Parkinson variance:
                 v = ln(H/L)^2 / (4 * ln2).
                 Range-only: no open/close term, so no clip
                 is needed (the term is always >= 0).
    pk_vol    -- sqrt(rolling mean of pk_var over 20 bars):
                 the realized-volatility estimate.
    pk_vol_sma -- SMA(pk_vol, 60): the slow volatility
                 baseline the expansion is measured against.
    ema20     -- EMA(close, 20): trend direction filter.
    atr14     -- Wilder ATR(14) for risk.

No lookahead: every column is a causal rolling/EWMA
function of bars up to and including the current one.
"""

import math

import numpy as np
import pandas as pd

from strategies import base as B

VOL_WINDOW = 20
VOL_SMA = 60
EMA_N = 20
ATR_N = 14


def add_indicators(
    df: pd.DataFrame,
    vol_window: int = VOL_WINDOW,
    vol_sma: int = VOL_SMA,
    ema_n: int = EMA_N,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    hl = np.log(df["h"] / df["l"])
    v = hl**2 / (4 * math.log(2))
    df["pk_var"] = v
    df["pk_vol"] = np.sqrt(
        v.rolling(vol_window, min_periods=vol_window).mean()
    )
    df["pk_vol_sma"] = B.sma(df["pk_vol"], vol_sma)
    df["ema20"] = B.ema(df["c"], ema_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
