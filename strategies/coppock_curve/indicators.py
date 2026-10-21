"""Coppock Curve indicators (E.S.C. Coppock, Barron's 1962).

Classic definition: Coppock = WMA(ROC(14) + ROC(11), 10), where
ROC(n) = 100 * (close / close.shift(n) - 1) and the WMA is linearly
weighted (newest bar gets the highest weight: weights w..1 over the
window, oldest -> newest, normalized).

HONEST MECHANICS NOTE: Coppock designed this for MONTHLY index
closes — the 14 and 11 lookbacks are the 11-to-14-month mourning
period he read about in church work. Applying (14, 11, 10) on 1h
crypto closes makes it a fast momentum oscillator, not a monthly
bottom-detector. It is shipped with the canonical (14, 11, 10)
anyway for comparability; see BACKTEST.md Limitations.

Columns:
    roc14   -- 100 * (c / c.shift(14) - 1)
    roc11   -- 100 * (c / c.shift(11) - 1)
    coppock -- WMA(roc14 + roc11, 10), linear weights
    atr     -- Wilder ATR(14) for sizing (consumed by the harness)

No lookahead: the value on bar j uses closes through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ROC_FAST = 11
ROC_SLOW = 14
WMA_N = 10


def wma(series: pd.Series, n: int) -> pd.Series:
    """Linear weighted MA: weight 1 (oldest) .. n (newest), normalized."""
    w = np.arange(1, n + 1, dtype=float)
    w = w / w.sum()
    x = series.to_numpy(dtype=float)

    def dot(win):
        return float(np.dot(w, win))

    return series.rolling(n, min_periods=n).apply(dot, raw=True)


def roc(close: pd.Series, n: int) -> pd.Series:
    """Rate of change in percent: 100 * (c / c.shift(n) - 1)."""
    prev = close.shift(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100.0 * (close / prev.replace(0.0, np.nan) - 1.0)
    return out


def coppock(close: pd.Series, n_fast: int = ROC_FAST, n_slow: int = ROC_SLOW,
            wma_n: int = WMA_N) -> pd.Series:
    """Coppock curve: WMA(ROC(n_slow) + ROC(n_fast), wma_n)."""
    return wma(roc(close, n_slow) + roc(close, n_fast), wma_n)


def add_indicators(df: pd.DataFrame, wma_n: int = WMA_N) -> pd.DataFrame:
    df = df.copy()
    df["roc14"] = roc(df["c"], ROC_SLOW)
    df["roc11"] = roc(df["c"], ROC_FAST)
    df["coppock"] = coppock(df["c"], ROC_FAST, ROC_SLOW, wma_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
