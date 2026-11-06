"""Stochastic Divergence signals: regular + hidden divergence on 5-bar
swing pivots.

A swing low is a bar whose low is the minimum of the centered 5-bar window
(bars i-2..i+2); a swing high is the mirror image. A pivot at index i is
only usable once confirmed, i.e. on bars >= i+2 — signals are emitted on
the confirmation bar (pivot index + 2), never on the unconfirmed pivot
itself. Divergence compares consecutive pivots no more than 40 bars apart,
using %K at the pivot bars: at most one entry per divergence pair.

Regular bullish: price lower low AND %K higher low -> long entry.
Regular bearish: price higher high AND %K lower high -> short entry.
Hidden bullish (uptrend, close > SMA(50) on the prior bar): price higher
low AND %K lower low -> long entry.
Hidden bearish (downtrend): price lower high AND %K higher high -> short
entry.
Exits: %K crosses above 80 (long), %K crosses below 20 (short).
"""

import numpy as np
import pandas as pd


def _pivot_indices(values: pd.Series, is_low: bool) -> list[int]:
    """Indices where values[i] is the extreme of the centered 5-bar window."""
    window = values.rolling(5, center=True, min_periods=5)
    extreme = window.min() if is_low else window.max()
    return [int(i) for i in range(len(values)) if values.iloc[i] == extreme.iloc[i]]


def _divergence_entries(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    n = len(df)
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    low = df["l"].to_numpy(dtype=float)
    high = df["h"].to_numpy(dtype=float)
    k = df["stoch_k"].to_numpy(dtype=float)
    close = df["c"].to_numpy(dtype=float)
    sma50 = df["sma50"].shift(1).to_numpy(dtype=float)

    for is_low, pivots in (
        (True, _pivot_indices(df["l"], True)),
        (False, _pivot_indices(df["h"], False)),
    ):
        for p1, p2 in zip(pivots, pivots[1:]):
            if p2 - p1 > 40 or p2 - p1 < 1:
                continue
            confirm = p2 + 2
            if confirm >= n:
                continue
            if not (np.isfinite(k[p1]) and np.isfinite(k[p2])):
                continue
            if is_low:
                price_ll = low[p2] < low[p1]
                price_hl = low[p2] > low[p1]
                k_hl = k[p2] > k[p1]
                k_ll = k[p2] < k[p1]
                if price_ll and k_hl:
                    long_entry[confirm] = True  # regular bullish
                elif price_hl and k_ll and np.isfinite(sma50[confirm]) and close[confirm] > sma50[confirm]:
                    long_entry[confirm] = True  # hidden bullish
            else:
                price_hh = high[p2] > high[p1]
                price_lh = high[p2] < high[p1]
                k_lh = k[p2] < k[p1]
                k_hh = k[p2] > k[p1]
                if price_hh and k_lh:
                    short_entry[confirm] = True  # regular bearish
                elif price_lh and k_hh and np.isfinite(sma50[confirm]) and close[confirm] < sma50[confirm]:
                    short_entry[confirm] = True  # hidden bearish
    return long_entry, short_entry


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry, short_entry = _divergence_entries(df)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    k = df["stoch_k"]
    prev_k = k.shift(1)
    df["long_exit"] = ((k > 80) & (prev_k <= 80)).fillna(False).astype(bool)
    df["short_exit"] = ((k < 20) & (prev_k >= 20)).fillna(False).astype(bool)
    return df
