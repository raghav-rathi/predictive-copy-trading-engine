"""CCI + MACD combo indicators.

CCI(14) on the typical price (h + l + c) / 3:

    CCI = (TP - SMA(TP, 14)) / (0.015 * mean_deviation)
    mean_deviation = mean(|TP - SMA(TP, 14)|) over the same 14 bars

A zero mean deviation (flat typical price) yields NaN CCI, which the
signal layer treats as no signal.

MACD(12, 26, 9) is computed on the raw close.

Columns:

    tp                    -- typical price (h + l + c) / 3
    tp_sma                -- 14-bar SMA of the typical price
    mean_dev              -- 14-bar mean absolute deviation of TP
    cci                   -- CCI(14)
    macd, macd_signal, macd_hist -- MACD(12, 26, 9) on close
    atr                   -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CCI_N = 14
CCI_CONST = 0.015
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["tp", "tp_sma", "mean_dev", "cci",
                  "macd", "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, n: int = CCI_N) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    tp_sma = tp.rolling(n, min_periods=n).mean()
    mean_dev = (tp - tp_sma).abs().rolling(n, min_periods=n).mean()
    denom = (CCI_CONST * mean_dev).replace(0, np.nan)
    cci = (tp - tp_sma) / denom
    df["tp"] = tp
    df["tp_sma"] = tp_sma
    df["mean_dev"] = mean_dev
    df["cci"] = cci
    macd = B.macd(df["c"], fast=MACD_FAST, slow=MACD_SLOW,
                  signal=MACD_SIGNAL)
    df["macd"] = macd["macd"]
    df["macd_signal"] = macd["macd_signal"]
    df["macd_hist"] = macd["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
