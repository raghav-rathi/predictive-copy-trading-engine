"""Stochastic Momentum Index indicators (William Blau, 1995).

Blau's SMI measures where the close sits relative to the midpoint of
the recent high/low range, double-smoothed:

    HH  = highest high over 13 bars
    LL  = lowest low over 13 bars
    D   = close - (HH + LL) / 2
    DS  = EMA(EMA(D, 25), 2)
    DHL = EMA(EMA(HH - LL, 25), 2)
    SMI = 100 * DS / (0.5 * DHL), clamped to [-100, 100]

The 13-bar range window and the 25/2 double smoothing are Blau's
published defaults (Momentum, Direction, and Divergence, 1995);
the 10,3,3 variant seen on some platforms is not used.

Columns:

    smi_hh, smi_ll  -- rolling 13-bar range extremes
    smi_d           -- raw distance from the range midpoint
    smi_ds          -- double-smoothed distance
    smi_dhl         -- double-smoothed range
    smi             -- Stochastic Momentum Index, [-100, 100]
    atr             -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
A zero range (DHL == 0, flat bars) yields SMI 0 rather than a
division-by-zero blow-up.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RANGE_N = 13
EMA_FAST = 25
EMA_SLOW = 2

INDICATOR_COLS = ["smi_hh", "smi_ll", "smi_d", "smi_ds", "smi_dhl",
                  "smi", "atr"]


def add_indicators(df: pd.DataFrame, n: int = RANGE_N,
                   ema_fast: int = EMA_FAST,
                   ema_slow: int = EMA_SLOW) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(n, min_periods=n).max()
    ll = df["l"].rolling(n, min_periods=n).min()
    d = df["c"] - (hh + ll) / 2
    ds = B.ema(B.ema(d, ema_fast), ema_slow)
    dhl = B.ema(B.ema(hh - ll, ema_fast), ema_slow)
    smi = 100.0 * ds / (0.5 * dhl.replace(0, np.nan))
    df["smi_hh"] = hh
    df["smi_ll"] = ll
    df["smi_d"] = d
    df["smi_ds"] = ds
    df["smi_dhl"] = dhl
    df["smi"] = smi.clip(-100.0, 100.0).fillna(0.0)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
