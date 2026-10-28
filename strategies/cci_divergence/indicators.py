"""CCI(20) pivot divergence indicators (causal, 2-bar pivot lag).

CCI = (typical price - SMA20(typical price)) / (0.015 * mean
deviation over 20 bars), Donald Lambert's construction. Price
pivots use the same 2-bar lag as triple_top_bottom: a pivot
centered at j is confirmed at bar j+2 and only then enters the
pivot lists, so a divergence bar never reads unconfirmed data.
The CCI value attached to a pivot is the CCI at the pivot bar
itself, which is long since known by confirmation time.

Columns:
    cci          -- CCI(20)
    cci_div_dir  -- +1 on a confirmed bullish divergence bar,
                    -1 on a confirmed bearish divergence bar, else 0
    atr          -- Wilder ATR(14) for the risk layer

Bullish: price makes a lower pivot low while CCI makes a higher
pivot low within 40 bars, confirmed by a close above the prior
3-bar high within 20 bars of the second pivot. Bearish mirrors.
"""

import numpy as np
import pandas as pd

from strategies import base as B

LAG = 2
CCI_N = 20
WINDOW = 40
CONFIRM_BARS = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    tp = (df["h"] + df["l"] + df["c"]) / 3
    sma = tp.rolling(CCI_N, min_periods=CCI_N).mean()
    # Standard Lambert mean deviation: mean |tp_j - SMA_k| over the
    # window ending at k (around the CURRENT bar's SMA, not a rolling
    # mean of per-bar deviations, which would delay CCI by 20 bars).
    tp_v = tp.to_numpy(dtype=float)
    sma_v = sma.to_numpy(dtype=float)
    md_v = np.full(n, np.nan)
    for k in range(CCI_N - 1, n):
        if np.isfinite(sma_v[k]):
            md_v[k] = np.mean(np.abs(tp_v[k - CCI_N + 1:k + 1] - sma_v[k]))
    with np.errstate(invalid="ignore", divide="ignore"):
        cci = ((tp_v - sma_v) / (0.015 * md_v))

    highs: list[tuple[int, float, float]] = []  # (bar, price, cci)
    lows: list[tuple[int, float, float]] = []
    fired: set[tuple[int, int, str]] = set()
    direction = np.zeros(n, dtype=int)

    for i in range(n):
        j = i - LAG
        if 2 <= j < n:
            if h[j] >= np.max(h[j - 2:j + 3]):
                if highs and j - highs[-1][0] <= LAG:
                    if h[j] > highs[-1][1]:
                        highs[-1] = (j, float(h[j]), float(cci[j]))
                else:
                    highs.append((j, float(h[j]), float(cci[j])))
            if l[j] <= np.min(l[j - 2:j + 3]):
                if lows and j - lows[-1][0] <= LAG:
                    if l[j] < lows[-1][1]:
                        lows[-1] = (j, float(l[j]), float(cci[j]))
                else:
                    lows.append((j, float(l[j]), float(cci[j])))

        # bullish: lower price low, higher CCI low
        if len(lows) >= 2 and i >= 3:
            p1, p2 = lows[-2], lows[-1]
            key = (p1[0], p2[0], "bull")
            if (
                p2[0] - p1[0] <= WINDOW
                and i - p2[0] <= CONFIRM_BARS
                and p2[1] < p1[1]
                and np.isfinite(p1[2]) and np.isfinite(p2[2]) and p2[2] > p1[2]
                and c[i] > np.max(h[i - 3:i])
                and key not in fired
            ):
                direction[i] = 1
                fired.add(key)

        # bearish: higher price high, lower CCI high
        if len(highs) >= 2 and i >= 3:
            p1, p2 = highs[-2], highs[-1]
            key = (p1[0], p2[0], "bear")
            if (
                p2[0] - p1[0] <= WINDOW
                and i - p2[0] <= CONFIRM_BARS
                and p2[1] > p1[1]
                and np.isfinite(p1[2]) and np.isfinite(p2[2]) and p2[2] < p1[2]
                and c[i] < np.min(l[i - 3:i])
                and key not in fired
            ):
                direction[i] = -1
                fired.add(key)

    df["cci"] = cci
    df["cci_div_dir"] = direction
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
