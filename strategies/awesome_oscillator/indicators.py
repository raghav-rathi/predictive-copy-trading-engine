"""Awesome Oscillator indicators (Bill Williams, "Trading Chaos").

AO = SMA(median_price, 5) - SMA(median_price, 34), median = (h + l) / 2.

Detectors (no lookahead: every value on bar i uses bars through i only):
  * saucer: three consecutive bars on one side of zero with the middle
    bar the extremum and the last bar turning back toward zero.
  * twin_peaks: within the last 30 bars, two strict local extrema on one
    side of zero, the second closer to zero than the first, AO never
    crossing the zero line inside the window, and AO rising/falling on
    the current bar after the second extremum.
"""

import numpy as np
import pandas as pd

from strategies import base as B

AO_FAST = 5
AO_SLOW = 34
TWIN_PEAK_LOOKBACK = 30


def _local_minima(arr: np.ndarray, lo: int, hi: int) -> list[tuple[int, float]]:
    """Strict local minima indices/values in [lo, hi], needing one bar each side."""
    out = []
    for j in range(lo + 1, hi):
        if arr[j] < arr[j - 1] and arr[j] < arr[j + 1]:
            out.append((j, arr[j]))
    return out


def _local_maxima(arr: np.ndarray, lo: int, hi: int) -> list[tuple[int, float]]:
    """Strict local maxima indices/values in [lo, hi], needing one bar each side."""
    out = []
    for j in range(lo + 1, hi):
        if arr[j] > arr[j - 1] and arr[j] > arr[j + 1]:
            out.append((j, arr[j]))
    return out


def _twin_peaks(ao: np.ndarray, lookback: int = TWIN_PEAK_LOOKBACK):
    """Return (bull, bear) boolean arrays of the twin-peaks pattern.

    Bullish twin peaks on bar i: the last two strict local minima of AO
    within bars [i-lookback+1, i-1] are both below 0, the second is
    higher (closer to zero) than the first, AO never crossed above 0
    inside the window, and AO[i] > AO[i-1] (rising after the second
    trough). Bearish is the mirror. NaN-safe: windows touching NaN are
    skipped.
    """
    n = len(ao)
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)
    for i in range(n):
        lo = i - lookback + 1
        if lo < 1:
            continue
        win = ao[lo : i + 1]
        if np.isnan(win).any():
            continue
        # ---- bullish: troughs below zero ----
        if win.max() <= 0:
            mins = _local_minima(ao, lo, i - 1)
            if len(mins) >= 2:
                (j1, v1), (j2, v2) = mins[-2], mins[-1]
                if v2 > v1 and ao[i] > ao[i - 1]:
                    bull[i] = True
        # ---- bearish: peaks above zero ----
        if win.min() >= 0:
            maxs = _local_maxima(ao, lo, i - 1)
            if len(maxs) >= 2:
                (j1, v1), (j2, v2) = maxs[-2], maxs[-1]
                if v2 < v1 and ao[i] < ao[i - 1]:
                    bear[i] = True
    return bull, bear


def add_indicators(
    df: pd.DataFrame,
    fast: int = AO_FAST,
    slow: int = AO_SLOW,
    lookback: int = TWIN_PEAK_LOOKBACK,
) -> pd.DataFrame:
    df = df.copy()
    median = (df["h"] + df["l"]) / 2
    ao = B.sma(median, fast) - B.sma(median, slow)
    df["ao"] = ao
    a0, a1, a2 = ao, ao.shift(1), ao.shift(2)
    df["bull_saucer"] = ((a0 > 0) & (a1 > 0) & (a2 > 0) & (a2 > a1) & (a1 < a0)).fillna(False)
    df["bear_saucer"] = ((a0 < 0) & (a1 < 0) & (a2 < 0) & (a2 < a1) & (a1 > a0)).fillna(False)
    bull_peaks, bear_peaks = _twin_peaks(ao.to_numpy(), lookback)
    df["bull_twin_peaks"] = pd.Series(bull_peaks, index=df.index)
    df["bear_twin_peaks"] = pd.Series(bear_peaks, index=df.index)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
