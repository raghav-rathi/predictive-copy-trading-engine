"""Garman-Klass realized-volatility indicators (Garman & Klass 1980).

    gk_var    -- per-bar Garman-Klass variance:
                 v = 0.5 * ln(H/L)^2 - (2*ln2 - 1) * ln(C/O)^2,
                 clipped at >= 0 PER BAR (before averaging).
                 The open/close term corrects the Parkinson
                 range term for drift; the clip keeps the
                 variance estimate non-negative.
    gk_vol    -- sqrt(rolling mean of gk_var over 20 bars):
                 the realized-volatility estimate.
    gk_vol_sma -- SMA(gk_vol, 60): the slow volatility
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
    co = np.log(df["c"] / df["o"])
    # Per-bar GK variance, clipped at zero BEFORE averaging.
    v = 0.5 * hl**2 - (2 * math.log(2) - 1) * co**2
    v = v.clip(lower=0.0)
    df["gk_var"] = v
    df["gk_vol"] = np.sqrt(
        v.rolling(vol_window, min_periods=vol_window).mean()
    )
    df["gk_vol_sma"] = B.sma(df["gk_vol"], vol_sma)
    df["ema20"] = B.ema(df["c"], ema_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
