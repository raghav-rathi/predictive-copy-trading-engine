"""Martin Pring's Know Sure Thing (KST) indicators.

KST = 1*RCMA(ROC10) + 2*RCMA(ROC15) + 3*RCMA(ROC20) + 4*RCMA(ROC30),
where RCMA is the 10-bar SMA of each rate-of-change (15-bar SMA for the
ROC30 leg) and ROCn = 100*(close - close[n])/close[n]. The weighted sum
of four smoothed momentum rates makes KST a broad momentum oscillator;
the 9-bar SMA signal line times entries. All causal: only data through
bar i's close.
"""

import pandas as pd

from strategies import base as B

ROC_PERIODS = (10, 15, 20, 30)
RCMA_PERIODS = (10, 10, 10, 15)
WEIGHTS = (1, 2, 3, 4)
SIGNAL = 9  # classic signal-line period


def _roc(c: pd.Series, n: int) -> pd.Series:
    return 100.0 * (c - c.shift(n)) / c.shift(n).replace(0, float("nan"))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    kst = 0.0
    for n, m, w in zip(ROC_PERIODS, RCMA_PERIODS, WEIGHTS):
        kst = kst + w * B.sma(_roc(c, n), m)
    df["kst"] = kst
    df["kst_signal"] = B.sma(kst, SIGNAL)
    return df
