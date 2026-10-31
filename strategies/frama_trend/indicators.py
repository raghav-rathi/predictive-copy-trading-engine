"""John Ehlers Fractal Adaptive Moving Average (FRAMA), N=16.

price = (H + L) / 2.
N1 = (highest high - lowest low over the most recent 8 bars) / 8.
N2 = (highest high - lowest low over the preceding 8 bars) / 8.
N3 = (highest high - lowest low over all 16 bars) / 16.
D = (log(N1 + N2) - log(N3)) / log(2), clamped to [1, 2].
alpha = exp(-4.6 * (D - 1)), clamped to [0.01, 1].
FRAMA = alpha * price + (1 - alpha) * prev FRAMA, initialised to the
price at the first valid bar (bar 15).

All windows end at the current bar; the "preceding 8 bars" window is
the shifted series, so no lookahead. A zero range (perfectly flat
prices) makes D undefined; it is treated as D = 2 (maximum congestion,
slowest adaptation), which is also what the clamp would give for a
fully congested market.

Columns:
    frama_price -- (H + L) / 2
    frama_n1, frama_n2, frama_n3 -- per-bar range components
    frama_dim  -- fractal dimension D, clamped [1, 2]
    frama_alpha -- smoothing factor, clamped [0.01, 1]
    frama      -- the adaptive average
    atr        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 16
HALF = 8


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    n = len(df)

    price = (h + l) / 2.0
    n1 = (h.rolling(HALF, min_periods=HALF).max()
          - l.rolling(HALF, min_periods=HALF).min()) / HALF
    n2 = (h.shift(HALF).rolling(HALF, min_periods=HALF).max()
          - l.shift(HALF).rolling(HALF, min_periods=HALF).min()) / HALF
    n3 = (h.rolling(N, min_periods=N).max()
          - l.rolling(N, min_periods=N).min()) / N

    n1v = n1.to_numpy(dtype=float)
    n2v = n2.to_numpy(dtype=float)
    n3v = n3.to_numpy(dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        dim = (np.log(n1v + n2v) - np.log(n3v)) / np.log(2.0)
    # Undefined (zero range) -> full congestion, D = 2; then clamp.
    dim = np.where(np.isfinite(dim), dim, 2.0)
    dim = np.clip(dim, 1.0, 2.0)
    alpha = np.exp(-4.6 * (dim - 1.0))
    alpha = np.clip(alpha, 0.01, 1.0)
    # Alpha is only defined once all three ranges are defined (bar 15).
    valid = (
        np.isfinite(n1v) & np.isfinite(n2v) & np.isfinite(n3v)
    )
    alpha = np.where(valid, alpha, np.nan)

    pv = price.to_numpy(dtype=float)
    frama = np.full(n, np.nan)
    first = np.where(valid)[0]
    if len(first):
        j = int(first[0])
        frama[j] = pv[j]
        for i in range(j + 1, n):
            a = alpha[i]
            frama[i] = a * pv[i] + (1.0 - a) * frama[i - 1]

    df["frama_price"] = price
    df["frama_n1"] = n1
    df["frama_n2"] = n2
    df["frama_n3"] = n3
    df["frama_dim"] = np.where(valid, dim, np.nan)
    df["frama_alpha"] = alpha
    df["frama"] = frama
    df["atr"] = B.atr(h, l, c, 14)
    return df
