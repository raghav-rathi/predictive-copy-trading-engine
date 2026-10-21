"""Know Sure Thing (KST) indicators (Martin Pring).

KST = 1*SMA(ROC(10),10) + 2*SMA(ROC(15),10) + 3*SMA(ROC(20),10)
      + 4*SMA(ROC(30),15),
where ROC(n) = 100 * (close / close.shift(n) - 1) and the SMA is a
plain 10- or 15-bar simple moving average of the raw ROC series
(Pring's original uses SMA on each ROC; some variants use WMA — the
SMA form is shipped).

signal = SMA(KST, 9): the standard trigger line.

Columns:
    roc10, roc15, roc20, roc30 -- raw rates of change (percent)
    rcma1..rcma4 -- SMA(ROC(n), n_smooth) for the four timeframes
    kst    -- weighted sum, weights 1/2/3/4 (the longest timeframe
              dominates)
    kst_signal -- SMA(kst, 9)
    atr    -- Wilder ATR(14) for sizing (consumed by the harness)

No lookahead: the value on bar j uses closes through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ROC_NS = (10, 15, 20, 30)
SMOOTH_NS = (10, 10, 10, 15)
WEIGHTS = (1, 2, 3, 4)
SIGNAL_N = 9


def roc(close: pd.Series, n: int) -> pd.Series:
    """Rate of change in percent: 100 * (c / c.shift(n) - 1)."""
    prev = close.shift(n)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = 100.0 * (close / prev.replace(0.0, np.nan) - 1.0)
    return out


def kst(close: pd.Series, signal_n: int = SIGNAL_N) -> pd.DataFrame:
    """KST + signal line, standard (10,15,20,30)/(10,10,10,15) weights 1-4."""
    c = pd.Series(close.to_numpy(dtype=float), index=close.index)
    parts = []
    for n, m, w in zip(ROC_NS, SMOOTH_NS, WEIGHTS):
        r = roc(c, n)
        s = r.rolling(m, min_periods=m).mean()
        parts.append(w * s)
    out = pd.DataFrame(index=close.index)
    out["kst"] = sum(parts)
    out["kst_signal"] = out["kst"].rolling(signal_n, min_periods=signal_n).mean()
    return out


def add_indicators(df: pd.DataFrame, signal_n: int = SIGNAL_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    out = kst(c, signal_n)
    df["kst"] = out["kst"]
    df["kst_signal"] = out["kst_signal"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
