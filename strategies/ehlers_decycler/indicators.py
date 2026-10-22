"""Decycler -- John Ehlers' trend extractor (TASC, Sep 2015).

The Decycler strips cycles out of price with a 2-pole Butterworth
high-pass filter and subtracts the cyclic component from the close,
leaving only the trend (low-pass) component:

    w     = 0.707 * 2*pi / P            (P = cutoff period, bars)
    alpha = (cos(w) + sin(w) - 1) / cos(w)
    hp[i] = (1 - alpha/2)^2 * (p[i] - 2*p[i-1] + p[i-2])
            + 2*(1-alpha)*hp[i-1] - (1-alpha)^2*hp[i-2]
    decycler = close - hp

Cycles shorter than the cutoff period P pass through the high-pass
filter and are removed; slower components (trend) stay in the
decycler line, which is zero-lag by construction for passed
frequencies. Columns:

    hp        -- the 2-pole high-pass filter output (cyclic component)
    decycler  -- close minus hp (the trend component)
    alpha     -- filter coefficient for the chosen period (scalar col)
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: hp[i] uses prices and hp values through bar i only;
hp[0] = hp[1] = 0 initializes the recursion.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CUTOFF_P = 20  # shipped default cutoff period, bars


def filter_alpha(period: int = CUTOFF_P) -> float:
    """The Butterworth 2-pole high-pass coefficient for a cutoff period."""
    w = 0.707 * 2.0 * np.pi / period
    return (np.cos(w) + np.sin(w) - 1.0) / np.cos(w)


def highpass(price: np.ndarray, alpha: float) -> np.ndarray:
    """2-pole Butterworth high-pass of a price array; hp[0..1] = 0."""
    hp = np.zeros(len(price))
    a1 = 1.0 - alpha / 2.0
    a2 = 1.0 - alpha
    for i in range(2, len(price)):
        hp[i] = (
            a1 * a1 * (price[i] - 2.0 * price[i - 1] + price[i - 2])
            + 2.0 * a2 * hp[i - 1]
            - a2 * a2 * hp[i - 2]
        )
    return hp


def add_indicators(df: pd.DataFrame, period: int = CUTOFF_P) -> pd.DataFrame:
    df = df.copy()
    alpha = filter_alpha(period)
    c = df["c"].to_numpy(dtype=float)
    hp = highpass(c, alpha)
    df["hp"] = hp
    df["decycler"] = c - hp
    df["alpha"] = alpha
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
