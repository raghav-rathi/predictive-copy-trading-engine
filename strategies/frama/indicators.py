"""FRAMA indicators (John Ehlers, Fractal Adaptive Moving Average).

Split the last N bars (N even) into two halves:
  N1 = (HH - LL of the recent N/2 bars) / (N/2)
  N2 = (HH - LL of the older  N/2 bars) / (N/2)
  N3 = (HH - LL of the whole  N   bars) / N
Fractal dimension D = (log(N1+N2) - log(N3)) / log(2), clamped to [1, 2].
alpha = exp(-4.6 * (D - 1)), clamped to [0.01, 1]: D=1 (straight trend)
means alpha~1 (fast), D=2 (space-filling chop) means alpha~0.01 (slow).
FRAMA = alpha * price + (1 - alpha) * FRAMA(prev), price = (h+l)/2.
All causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 16  # must be even
SLOW_N = 100  # slow SMA gate


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    price = ((df["h"] + df["l"]) / 2).to_numpy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    n = len(df)
    half = N // 2
    frama = np.full(n, np.nan)
    dimen = np.full(n, np.nan)
    if n > N:
        frama[N - 1] = price[N - 1]
        for i in range(N, n):
            w = slice(i - N + 1, i + 1)
            n3 = (h[w].max() - l[w].min()) / N
            n1 = (h[i - half + 1 : i + 1].max() - l[i - half + 1 : i + 1].min()) / half
            n2 = (h[i - N + 1 : i - half + 1].max() - l[i - N + 1 : i - half + 1].min()) / half
            if n1 > 0 and n2 > 0 and n3 > 0:
                d = (np.log(n1 + n2) - np.log(n3)) / np.log(2)
            else:
                d = 1.0
            d = min(max(d, 1.0), 2.0)
            alpha = min(max(np.exp(-4.6 * (d - 1.0)), 0.01), 1.0)
            dimen[i] = d
            frama[i] = alpha * price[i] + (1.0 - alpha) * frama[i - 1]
    df["frama"] = frama
    df["frama_dimen"] = dimen
    df["frama_slope"] = pd.Series(frama).diff(3)
    df["frama_slow"] = B.sma(df["c"], SLOW_N)
    return df
