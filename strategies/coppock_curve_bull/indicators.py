"""Coppock Curve indicators (Edwin Coppock, Barron's Oct 15, 1962).

The canonical monthly Coppock Curve is:

    Coppock = WMA(ROC(14) + ROC(11), 10)   (months)

i.e. the 10-month weighted moving average of the sum of the 14-month
and 11-month rates of change. The monthly original cannot fire on
~8 months of 1h data, so this build translates the lookbacks to
hours at 24h/day and documents the adaptation honestly:

    ROC lookbacks: 336h (14 days) and 264h (11 days)
    WMA window:    240h (10 days), front-weighted (newest weight 240
                   down to 1, oldest weight 1)

    ROC_n = 100 * (C_t - C_{t-n}) / C_{t-n}

Columns:
    roc14  -- 336h rate of change
    roc11  -- 264h rate of change
    coppock -- WMA(240) of roc14 + roc11
    turn_up   -- Coppock rises after falling (local trough)
    turn_down -- Coppock falls after rising (local peak)

No lookahead: ROC uses closes up to bar i only; the WMA is a
causal rolling window ending at bar i; turns compare bars i, i-1,
i-2 only.
"""

import numpy as np
import pandas as pd

ROC_LONG = 336   # 14 days in hours (monthly 14)
ROC_SHORT = 264  # 11 days in hours (monthly 11)
WMA_WINDOW = 240  # 10 days in hours (monthly 10)


def _wma(s: pd.Series, window: int) -> pd.Series:
    """Front-weighted WMA: newest bar gets weight ``window``, oldest 1."""
    w = np.arange(1, window + 1, dtype=float)  # [1, ..., window]: newest bar gets weight ``window``
    wsum = w.sum()
    return s.rolling(window, min_periods=window).apply(
        lambda x: float(np.dot(w, x)) / wsum, raw=True
    )


def add_indicators(
    df: pd.DataFrame,
    wma_window: int = WMA_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["roc14"] = 100.0 * (c - c.shift(ROC_LONG)) / c.shift(ROC_LONG)
    df["roc11"] = 100.0 * (c - c.shift(ROC_SHORT)) / c.shift(ROC_SHORT)
    df["coppock"] = _wma(df["roc14"] + df["roc11"], wma_window)
    cp = df["coppock"]
    df["turn_up"] = (cp > cp.shift(1)) & (cp.shift(1) <= cp.shift(2))
    df["turn_down"] = (cp < cp.shift(1)) & (cp.shift(1) >= cp.shift(2))
    return df
