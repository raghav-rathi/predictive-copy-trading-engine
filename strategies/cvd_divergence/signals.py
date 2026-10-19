"""CVD divergence signals (regular divergence only).

Bullish regular divergence: at a price pivot low on bar i, find the most
recent earlier price pivot low j within the trailing 60 bars; if price
made a lower low (c[i] < c[j]) while CVD made a higher low
(cvd[i] > cvd[j]), sellers are exhausted -> long.

Bearish regular divergence mirrors: price higher high vs CVD lower high
at a pivot high -> short.

Exits are the opposite divergence (a long exits when bearish divergence
prints, a short when bullish divergence prints); the harness also runs a
3xATR chandelier trailing stop from risk.py.

All signal columns are boolean, no NaN; execution at next-bar open is
handled by the harness.
"""

import numpy as np
import pandas as pd


def _divergence_flags(
    c: np.ndarray,
    cvd: np.ndarray,
    pivots: np.ndarray,
    lookback: int,
    bullish: bool,
) -> np.ndarray:
    """Mark pivot bars where price and CVD diverge vs the nearest earlier
    pivot inside ``lookback`` bars."""
    n = len(c)
    flags = np.zeros(n, dtype=bool)
    piv = np.where(pivots)[0]
    for i in piv:
        earlier = piv[(piv < i) & (piv >= i - lookback)]
        if len(earlier) == 0:
            continue
        j = earlier[-1]
        if bullish:
            if c[i] < c[j] and cvd[i] > cvd[j]:
                flags[i] = True
        else:
            if c[i] > c[j] and cvd[i] < cvd[j]:
                flags[i] = True
    return flags


def add_signals(df: pd.DataFrame, lookback: int = 60) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    cvd = df["cvd"].to_numpy(dtype=float)
    bull = _divergence_flags(
        c, cvd, df["pivot_low"].fillna(False).to_numpy(), lookback, bullish=True
    )
    bear = _divergence_flags(
        c, cvd, df["pivot_high"].fillna(False).to_numpy(), lookback, bullish=False
    )
    df["long_entry"] = pd.Series(bull, index=df.index).astype(bool)
    df["short_entry"] = pd.Series(bear, index=df.index).astype(bool)
    # exits: opposite divergence
    df["long_exit"] = pd.Series(bear, index=df.index).astype(bool)
    df["short_exit"] = pd.Series(bull, index=df.index).astype(bool)
    return df
