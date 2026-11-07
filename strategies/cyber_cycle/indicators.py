"""Cyber Cycle indicators: John Ehlers' Cyber Cycle (Cybernetic Analysis
for Stocks and Futures, ch. 4, 2004).

Smoothed price:  smooth = (c + 2*c1 + 2*c2 + c3) / 6
Cycle (alpha = 0.07):
    cycle = (1 - 0.5*alpha)^2 * (smooth - 2*smooth1 + smooth2)
            + 2*(1 - alpha)*cycle1 - (1 - alpha)^2 * cycle2
Signal: an EMA-style smoothing of the cycle with alpha2 = 0.1:
    Signal = alpha2*cycle + (1 - alpha2)*Signal1

All terms use only data through bar i's close; the cycle recursion is
seeded at zero, so the first ~100 bars are warmup (WARMUP = 100).
"""

import numpy as np
import pandas as pd

ALPHA = 0.07
ALPHA2 = 0.1

INDICATOR_COLS = ["cc_smooth", "cc_cycle", "cc_signal"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(c)
    smooth = np.full(n, np.nan)
    if n >= 4:
        smooth[3:] = (c[3:] + 2 * c[2:-1] + 2 * c[1:-2] + c[:-3]) / 6.0
    cycle = np.zeros(n)
    signal = np.zeros(n)
    a = 1.0 - 0.5 * ALPHA
    b = 1.0 - ALPHA
    # smooth is only defined from bar 3, so the cycle recursion (which
    # needs smooth[i], smooth[i-1], smooth[i-2]) starts at bar 5.
    for i in range(5, n):
        cycle[i] = (
            a * a * (smooth[i] - 2 * smooth[i - 1] + smooth[i - 2])
            + 2 * b * cycle[i - 1]
            - b * b * cycle[i - 2]
        )
        signal[i] = ALPHA2 * cycle[i] + (1.0 - ALPHA2) * signal[i - 1]
    df["cc_smooth"] = smooth
    df["cc_cycle"] = cycle
    df["cc_signal"] = signal
    return df
