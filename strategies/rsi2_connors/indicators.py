"""Connors RSI indicators.

Connors RSI (CRSI) = mean of three components, each on a 3-bar
window (per the batch spec; note the canonical Connors RSI uses
RSI(2) for the streak component -- see CALIBRATION.md):

  (a) RSI(3) of the close (Wilder, via strategies.base.rsi),
  (b) RSI(3) of the up/down streak series, where
          streak[i] = streak[i-1] + 1  if c[i] > c[i-1]
          streak[i] = streak[i-1] - 1  if c[i] < c[i-1]
          streak[i] = 0                if c[i] == c[i-1],
  (c) percentile rank of the 1-bar ROC over the trailing 100 bars:
      100 * (number of ROC values in the last 100 bars, including
      today, strictly below today's ROC) / 100.

Columns:
    streak -- up/down streak series
    rsi_price -- RSI(3) of close
    rsi_streak -- RSI(3) of the streak series
    roc1 -- 1-bar rate of change, percent
    pct_rank -- percentile rank of roc1 over the trailing 100 bars
    crsi -- Connors RSI, mean of (a), (b), (c)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. The percentile rank uses the trailing 100 ROC values
including today's; the first defined value is at bar 100 (the
window must be fully defined).
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 3
STREAK_N = 3
RANK_N = 100
ATR_N = 14


def _streak_series(c: pd.Series) -> pd.Series:
    cv = c.to_numpy(dtype=float)
    s = np.zeros(len(cv), dtype=float)
    for i in range(1, len(cv)):
        if cv[i] > cv[i - 1]:
            s[i] = s[i - 1] + 1
        elif cv[i] < cv[i - 1]:
            s[i] = s[i - 1] - 1
        else:
            s[i] = 0.0
    return pd.Series(s, index=c.index)


def _pct_rank(roc: pd.Series, n: int) -> pd.Series:
    vals = roc.to_numpy(dtype=float)
    out = np.full(len(vals), np.nan)
    for i in range(n - 1, len(vals)):
        w = vals[i - n + 1:i + 1]
        if np.isnan(w).any():
            continue
        out[i] = 100.0 * float(np.sum(w < vals[i])) / n
    return pd.Series(out, index=roc.index)


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_N,
                   streak_n: int = STREAK_N, rank_n: int = RANK_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    streak = _streak_series(c)
    df["streak"] = streak
    df["rsi_price"] = B.rsi(c, rsi_n)
    df["rsi_streak"] = B.rsi(streak, streak_n)
    df["roc1"] = c.diff() / c.shift(1) * 100.0
    df["pct_rank"] = _pct_rank(df["roc1"], rank_n)
    df["crsi"] = (df["rsi_price"] + df["rsi_streak"] + df["pct_rank"]) / 3.0
    df["atr"] = B.atr(df["h"], df["l"], c, atr_n)
    return df
