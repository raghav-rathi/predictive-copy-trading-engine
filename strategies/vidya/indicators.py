"""VIDYA indicators (Tushar Chande, The New Technical Trader).

CMO(n) = (UpSum - DnSum) / (UpSum + DnSum) over n bars, signed sums of
close-to-close changes.
VIDYA(i) = VIDYA(i-1) + F * |CMO| * (close(i) - VIDYA(i-1)),
with F = 2/(ema_period+1). Momentum-adaptive: fast in trends (|CMO|~1),
slow in chop (|CMO|~0). Also computes a slow SMA reference for the
directional gate. All causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CMO_N = 9
EMA_N = 12
SLOW_N = 50


def _cmo(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    up = d.clip(lower=0).rolling(n, min_periods=n).sum()
    dn = (-d.clip(upper=0)).rolling(n, min_periods=n).sum()
    denom = (up + dn).replace(0, np.nan)
    return ((up - dn) / denom).fillna(0.0)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    cmo = _cmo(c, CMO_N)
    f = 2.0 / (EMA_N + 1)
    alpha = (f * cmo.abs()).clip(0.0, 1.0).to_numpy()
    px = c.to_numpy()
    n = len(px)
    vid = np.full(n, np.nan)
    start = CMO_N
    if n > start:
        vid[start] = px[start]
        for i in range(start + 1, n):
            vid[i] = vid[i - 1] + alpha[i] * (px[i] - vid[i - 1])
    df["vidya"] = vid
    df["vidya_slope"] = pd.Series(vid).diff(5)
    df["vidya_slow"] = B.sma(c, SLOW_N)
    return df
