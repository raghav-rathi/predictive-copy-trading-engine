"""Ultimate Oscillator divergence signals (Williams' rules).

  Bullish divergence: price prints a lower 3-bar fractal swing low
    while UO prints a higher low there, AND UO dipped below 30 during
    the divergence window -> long at the close of the bar where the
    second swing low is confirmed.
  Bearish divergence: price prints a higher swing high, UO a lower
    high, UO exceeded 50 during the window -> short at confirmation.

  long_exit:  UO > 70 (overbought extreme)
  short_exit: UO < 30 (oversold extreme)

A k=3 fractal pivot centred at bar j is confirmed at bar j+3, and the
entry is placed there — never earlier. Both pivots must fall inside
a 120-bar window. Expect a low trade count: genuine divergences are
rare by construction.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_K = 3
DIV_WINDOW = 120
BULL_OS_LEVEL = 30.0   # UO must dip under this during a bullish divergence
BEAR_OB_LEVEL = 50.0   # UO must exceed this during a bearish divergence
LONG_EXIT_UO = 70.0
SHORT_EXIT_UO = 30.0


def _fractal_pivots(values: np.ndarray, k: int, kind: str) -> list:
    """Causal k-bar fractal pivots; ties resolve to the first bar so flat
    runs do not manufacture pivots."""
    n = len(values)
    out = []
    for j in range(k, n - k):
        w = values[j - k:j + k + 1]
        if kind == "low" and int(np.argmin(w)) == k:
            out.append(j)
        elif kind == "high" and int(np.argmax(w)) == k:
            out.append(j)
    return out


def _bull_divergence(lows, closes, uo, j2, window=DIV_WINDOW,
                     os_level=BULL_OS_LEVEL) -> bool:
    """True when the confirmed swing low at j2 diverges bullishly."""
    if np.isnan(uo[j2]):
        return False
    prev = [j for j in lows if j < j2 and j2 - j <= window]
    if not prev:
        return False
    j1 = prev[-1]
    if np.isnan(uo[j1]):
        return False
    if not closes[j2] < closes[j1]:      # price: lower low
        return False
    if not uo[j2] > uo[j1]:             # oscillator: higher low
        return False
    return bool(np.nanmin(uo[j1:j2 + 1]) < os_level)


def _bear_divergence(highs, closes, uo, j2, window=DIV_WINDOW,
                     ob_level=BEAR_OB_LEVEL) -> bool:
    """True when the confirmed swing high at j2 diverges bearishly."""
    if np.isnan(uo[j2]):
        return False
    prev = [j for j in highs if j < j2 and j2 - j <= window]
    if not prev:
        return False
    j1 = prev[-1]
    if np.isnan(uo[j1]):
        return False
    if not closes[j2] > closes[j1]:     # price: higher high
        return False
    if not uo[j2] < uo[j1]:             # oscillator: lower high
        return False
    return bool(np.nanmax(uo[j1:j2 + 1]) > ob_level)


def add_signals(df: pd.DataFrame, pivot_k: int = PIVOT_K,
                os_level: float = BULL_OS_LEVEL,
                ob_level: float = BEAR_OB_LEVEL) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    l = df["l"].to_numpy()
    h = df["h"].to_numpy()
    c = df["c"].to_numpy()
    uo = df["uo"].to_numpy()

    lows = _fractal_pivots(l, pivot_k, "low")
    highs = _fractal_pivots(h, pivot_k, "high")

    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    for j2 in lows:
        i = j2 + pivot_k  # confirmation bar
        if i < n and _bull_divergence(lows, c, uo, j2, os_level=os_level):
            long_entry[i] = True
    for j2 in highs:
        i = j2 + pivot_k
        if i < n and _bear_divergence(highs, c, uo, j2, ob_level=ob_level):
            short_entry[i] = True

    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = (df["uo"] > LONG_EXIT_UO).fillna(False).astype(bool)
    df["short_exit"] = (df["uo"] < SHORT_EXIT_UO).fillna(False).astype(bool)
    return df
