"""Quantitative Qualitative Estimation indicators (Glaz).

QQE = a smoothed RSI plus two volatility-based trailing levels:
  RSIndex   = EMA(RSI(14), SF=5)
  ATRrsi    = double-Wilders smoothing of |RSIndex - RSIndex[1]|
  delta     = QQE_FACTOR (4.236) * ATRrsi, computed on a fast (27) and
              a slow (54) Wilders window
  trailing  = the classic QQE ratchet: the long band only ever moves up
              while RSIndex stays above it, the short band only moves
              down while RSIndex stays below it; the active line follows
              the trend state.

The traded signal is the documented Fast-TL/Slow-TL cross. No lookahead:
bands and trend are computed strictly left-to-right on bars through i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_LEN = 14
SF = 5
WP_FAST = 27
WP_SLOW = 54
QQE_FACTOR = 4.236


def _wilders2(s: pd.Series, n: int) -> pd.Series:
    w1 = s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    return w1.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def _trailing_line(rsindex: np.ndarray, delta: np.ndarray) -> np.ndarray:
    """Causal QQE trailing line: trend +1 follows the long band, -1 the
    short band; trend flips when RSIndex crosses the opposite band."""
    n = len(rsindex)
    line = np.full(n, np.nan)
    lb = np.full(n, np.nan)
    sb = np.full(n, np.nan)
    trend = np.zeros(n, dtype=int)
    for i in range(n):
        r, d = rsindex[i], delta[i]
        if np.isnan(r) or np.isnan(d):
            continue
        new_lb, new_sb = r - d, r + d
        if i > 0 and not np.isnan(lb[i - 1]):
            pr, plb, psb, pt = rsindex[i - 1], lb[i - 1], sb[i - 1], trend[i - 1]
            if pr > plb and r > plb:
                new_lb = max(plb, new_lb)
            if pr < psb and r < psb:
                new_sb = min(psb, new_sb)
            if r > psb:
                t = 1
            elif r < plb:
                t = -1
            else:
                t = pt
        else:
            t = 0
        lb[i], sb[i], trend[i] = new_lb, new_sb, t
        line[i] = new_lb if t >= 0 else new_sb
    return line


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], RSI_LEN)
    rsindex = rsi.ewm(span=SF, adjust=False, min_periods=SF).mean()
    delta_fast = _wilders2(rsindex.diff().abs(), WP_FAST) * QQE_FACTOR
    delta_slow = _wilders2(rsindex.diff().abs(), WP_SLOW) * QQE_FACTOR
    df["qqe_rsindex"] = rsindex
    df["qqe_fast"] = _trailing_line(rsindex.to_numpy(), delta_fast.to_numpy())
    df["qqe_slow"] = _trailing_line(rsindex.to_numpy(), delta_slow.to_numpy())
    return df
