"""Reflex -- John Ehlers' zero-lag trend oscillator (TASC, Feb 2020).

Mechanism
---------
1. Smooth the close with Ehlers' 2-pole SuperSmoother:
       a1 = exp(-1.414 * pi / period)
       b1 = 2 * a1 * cos(1.414 * 180 / period)   (angle in degrees)
       c2 = b1, c3 = -a1^2, c1 = 1 - c2 - c3
       filt[i] = c1 * (x[i] + x[i-1]) / 2 + c2 * filt[i-1] + c3 * filt[i-2]
   The SuperSmoother strips high-frequency noise with less lag than a
   same-period EMA.

2. Detrend by linear extrapolation:
       Slope = (filt - filt.shift(L)) / L
       Sum   = sum_{k=1..L} ((filt + k * Slope) - filt.shift(k))
   ``filt + k*Slope`` is where the locally linear trend says price
   should be now; subtracting the smoothed price k bars ago and
   summing over the whole lookback cancels the smoothing lag, so the
   Sum series turns almost as soon as the underlying trend does.

3. Normalize by its own running variance:
       MS     = 0.04 * Sum^2 + 0.96 * MS.shift(1)   (recursive EMA; MS=Sum^2 on the seed bar)
       Reflex = Sum / sqrt(MS)                      (0/0 guarded to NaN)

Because the numerator is detrended (zero-lag) and the denominator is
the local variance of that detrended series, Reflex is a self-scaling
oscillator: on chop the Sum mean-reverts and MS floors, keeping
Reflex bounded near zero; on a sustained trend the Sum term
dominates and Reflex pins to one sign. Zero crosses mark confirmed
trend turns.

Columns added: ``filt`` (SuperSmoother output), ``reflex``,
``sum_`` (raw detrended sum), ``ms``, ``atr`` (Wilder ATR(14) for
the risk layer).

No lookahead: the SuperSmoother uses closes through bar i only, and
every shift is strictly into the past.
"""

import numpy as np
import pandas as pd

from strategies import base as B

REFLEX_LEN = 20  # shipped default, fixed a priori
MS_ALPHA = 0.04  # variance-EMA smoothing, per Ehlers


def supersmoother(x: np.ndarray, period: int) -> np.ndarray:
    """Ehlers 2-pole SuperSmoother.

    Cold start matches Ehlers' NZ(Filt[1], Price) convention: the
    filter value collapses to the current price on the first bar, so
    the transient is short and everything is warm by WARMUP=100.
    """
    x = np.asarray(x, dtype=float)
    a1 = np.exp(-1.414 * np.pi / period)
    b1 = 2.0 * a1 * np.cos(np.deg2rad(1.414 * 180.0 / period))
    c2 = b1
    c3 = -a1 * a1
    c1 = 1.0 - c2 - c3
    filt = np.empty(len(x))
    filt[0] = x[0]
    for i in range(1, len(x)):
        prev2 = filt[i - 2] if i > 1 else x[0]
        filt[i] = c1 * (x[i] + x[i - 1]) / 2.0 + c2 * filt[i - 1] + c3 * prev2
    return filt


def reflex(close: pd.Series, length: int = REFLEX_LEN) -> pd.DataFrame:
    """Reflex oscillator from the close series."""
    filt_arr = supersmoother(close.to_numpy(), length)
    filt = pd.Series(filt_arr, index=close.index)
    slope = (filt - filt.shift(length)) / length
    sum_ = pd.Series(0.0, index=close.index)
    for k in range(1, length + 1):
        sum_ = sum_ + ((filt + k * slope) - filt.shift(k))
    sum2 = sum_ ** 2
    # Recursive variance EMA; adjust=False seeds MS with the first
    # valid Sum^2 value, exactly Ehlers' MS=Sum^2 initialization.
    ms = sum2.ewm(alpha=MS_ALPHA, adjust=False, min_periods=1).mean()
    denom = np.sqrt(ms).replace(0.0, np.nan)  # div-by-zero guard
    rx = sum_ / denom
    return pd.DataFrame({"filt": filt, "sum_": sum_, "ms": ms, "reflex": rx})


def add_indicators(df: pd.DataFrame, length: int = REFLEX_LEN) -> pd.DataFrame:
    df = df.copy()
    r = reflex(df["c"], length)
    df["filt"] = r["filt"]
    df["sum_"] = r["sum_"]
    df["ms"] = r["ms"]
    df["reflex"] = r["reflex"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
