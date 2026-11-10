"""Hans Hannula's Polarized Fractal Efficiency (PFE) indicator.

Faithful transcription of the formula from Hans Hannula, "Polarized
Fractal Efficiency", Technical Analysis of Stocks & Commodities,
January 1994 (see also https://www.investopedia.com/terms/p/pfe.asp
and https://docs.wickra.org/Indicators/Indicator-PolarizedFractalEfficiency).

With lookback N = 10 and smoothing M = 5, all causal (bar i uses only
data through bar i's close):

  straight_t = sqrt((close_t - close_{t-10})^2 + 10^2)
      -- direct n-bar distance; each bar counts as 1 unit on the x-axis.
  path_t = sum over i=1..10 of sqrt((close_{t-i+1} - close_{t-i})^2 + 1)
      -- summed single-bar step distances.
  raw_t = 100 * sign(close_t - close_{t-10}) * straight_t / path_t
      -- sign +1 if close_t >= close_{t-10}, else -1; path == 0 -> 0.
  PFE_t = EMA(raw, 5), bounded [-100, +100].

Near 0 = chop (path much longer than the straight-line distance),
+100 = clean up-move, -100 = clean down-move.
"""

import math

import numpy as np
import pandas as pd

from strategies.base import ema

N = 10
SMOOTHING = 5

INDICATOR_COLS = [
    "pfe",
    "pfe_raw",
    "pfe_straight",
    "pfe_path",
]


def _pfe_raw(close: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (raw, straight, path); NaN for the first N bars."""
    n = len(close)
    raw = np.full(n, np.nan)
    straight = np.full(n, np.nan)
    path = np.full(n, np.nan)
    for t in range(N, n):
        diff_n = float(close[t] - close[t - N])
        s = math.sqrt(diff_n * diff_n + N * N)
        p = 0.0
        for i in range(1, N + 1):
            step = float(close[t - i + 1] - close[t - i])
            p += math.sqrt(step * step + 1.0)
        straight[t] = s
        path[t] = p
        if p == 0.0:
            raw[t] = 0.0
        else:
            sign = 1.0 if diff_n >= 0.0 else -1.0
            raw[t] = 100.0 * sign * s / p
    return raw, straight, path


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["c"].to_numpy(dtype=float)
    raw, straight, path = _pfe_raw(close)
    df["pfe_raw"] = raw
    df["pfe_straight"] = straight
    df["pfe_path"] = path
    # EMA(span=5, adjust=False, min_periods=5): first PFE at bar N+4.
    df["pfe"] = ema(pd.Series(raw, index=df.index), SMOOTHING)
    return df
