"""MACD with Kaufman efficiency-ratio adaptive EMAs.

Efficiency ratio over ER_N bars:
    ER = |close - close[ER_N]| / sum(|close diffs| over ER_N bars)
(ER = 0 on a flat stretch where the denominator is 0.)

KAMA-style smoothing constants, fast range 2..12 and slow range
5..26:
    SC_fast = (ER * (2/3 - 2/13) + 2/13) ** 2
    SC_slow = (ER * (2/6 - 2/27) + 2/27) ** 2
Adaptive EMA recursion: EMA[i] = EMA[i-1] + SC[i] * (close[i] -
EMA[i-1]), seeded with the close on the first bar where ER is
defined. MACD line = fast adaptive EMA - slow adaptive EMA;
signal = 9-bar EMA of the MACD line (alpha 2/10, seeded with the
first MACD value).

Columns:
    er -- efficiency ratio
    sc_fast / sc_slow -- adaptive smoothing constants
    ama_fast / ama_slow -- adaptive EMAs
    macd / macd_signal / macd_hist
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. ER uses closes through bar i; the recursions step forward
one bar at a time.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ER_N = 10
FAST_MIN = 2
FAST_MAX = 12
SLOW_MIN = 5
SLOW_MAX = 26
SIGNAL_N = 9
ATR_N = 14


def _sc(er: np.ndarray, lo: int, hi: int) -> np.ndarray:
    """KAMA smoothing constant for period range lo..hi."""
    fast_sc = 2.0 / (lo + 1)
    slow_sc = 2.0 / (hi + 1)
    return (er * (fast_sc - slow_sc) + slow_sc) ** 2


def _adaptive_ema(c: np.ndarray, sc: np.ndarray, start: int) -> np.ndarray:
    """Recursive adaptive EMA, seeded with close[start]."""
    out = np.full(len(c), np.nan)
    if start >= len(c):
        return out
    out[start] = c[start]
    for i in range(start + 1, len(c)):
        out[i] = out[i - 1] + sc[i] * (c[i] - out[i - 1])
    return out


def add_indicators(df: pd.DataFrame, er_n: int = ER_N,
                   signal_n: int = SIGNAL_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    abs_diff = np.abs(np.diff(c, prepend=c[0]))
    # sum of |diffs| over the trailing er_n bars (bars i-er_n+1 .. i)
    denom = pd.Series(abs_diff).rolling(er_n, min_periods=er_n).sum().to_numpy(dtype=float)
    numer = np.full(n, np.nan)
    numer[er_n:] = np.abs(c[er_n:] - c[:-er_n])
    er = np.where(denom > 0, numer / np.where(denom > 0, denom, 1.0), 0.0)
    er[:er_n] = np.nan
    df["er"] = er

    sc_fast = _sc(np.nan_to_num(er, nan=0.0), FAST_MIN, FAST_MAX)
    sc_slow = _sc(np.nan_to_num(er, nan=0.0), SLOW_MIN, SLOW_MAX)
    df["sc_fast"] = np.where(np.isnan(er), np.nan, sc_fast)
    df["sc_slow"] = np.where(np.isnan(er), np.nan, sc_slow)

    start = er_n
    ama_fast = _adaptive_ema(c, sc_fast, start)
    ama_slow = _adaptive_ema(c, sc_slow, start)
    df["ama_fast"] = ama_fast
    df["ama_slow"] = ama_slow

    macd_line = ama_fast - ama_slow
    df["macd"] = macd_line
    # Signal: 9-bar EMA of MACD, seeded with the first MACD value.
    sig = np.full(n, np.nan)
    alpha = 2.0 / (signal_n + 1)
    if start < n:
        sig[start] = macd_line[start]
        for i in range(start + 1, n):
            sig[i] = sig[i - 1] + alpha * (macd_line[i] - sig[i - 1])
    df["macd_signal"] = sig
    df["macd_hist"] = macd_line - sig
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
