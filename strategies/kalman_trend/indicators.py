"""Kalman filter trend indicators.

1-D Kalman filter with a velocity state on closes: x = [price, velocity].

    F = [[1, 1], [0, 1]]   (constant-velocity transition)
    H = [1, 0]             (observe price only)
    Q = diag(0.05, 0.01)   (process noise: price jitter, velocity drift)
    R = r                  (measurement noise, shipped r = 1.0)

Init: x = [first close, 0], P = diag(1, 1).

Per bar with measurement z = close[i]:
    predict: x = F @ x ;  P = F @ P @ F.T + Q
    update:  y = z - x[0];  S = P[0,0] + R;  K = P[:,0] / S
             x = x + K * y;  P = P - outer(K, P[0,:])
    kf[i] = x[0]

The velocity state lets the filter lag less than a plain SMA in a
steady drift while still damping chop: the filter believes sustained
moves, doubts one-bar spikes.

Columns:
  kf       -- Kalman filter price estimate
  kf_slope -- kf[i] - kf[i-1] (first bar: 0)
  atr      -- ATR(14) for the risk layer

No lookahead: bar i's kf uses only closes through bar i.
Pure numpy loop (~5.2k bars: fast). No TA-Lib.
"""

import numpy as np
import pandas as pd

from strategies import base as B

Q_PRICE = 0.05
Q_VEL = 0.01
R_DEFAULT = 1.0


def _kalman(closes: np.ndarray, r: float) -> np.ndarray:
    """Single numpy loop. Returns the kf price-estimate series."""
    n = len(closes)
    kf = np.empty(n, dtype=float)
    if n == 0:
        return kf
    x = np.array([closes[0], 0.0], dtype=float)
    P = np.eye(2, dtype=float)
    Q = np.diag([Q_PRICE, Q_VEL])
    for i in range(n):
        z = closes[i]
        # predict
        x0 = x[0] + x[1]
        x1 = x[1]
        # P = F P F.T + Q  with F = [[1,1],[0,1]]
        p00 = P[0, 0] + P[0, 1] + P[1, 0] + P[1, 1] + Q[0, 0]
        p01 = P[0, 1] + P[1, 1]
        p10 = P[1, 0] + P[1, 1]
        p11 = P[1, 1] + Q[1, 1]
        x = np.array([x0, x1])
        # update
        y = z - x[0]
        S = p00 + r
        k0 = p00 / S
        k1 = p10 / S
        x = x + np.array([k0, k1]) * y
        # P = P - outer(K, P[0,:])  with row0 = [p00, p01]
        P = np.array(
            [
                [p00 - k0 * p00, p01 - k0 * p01],
                [p10 - k1 * p00, p11 - k1 * p01],
            ]
        )
        kf[i] = x[0]
    return kf


def add_indicators(df: pd.DataFrame, r: float = R_DEFAULT) -> pd.DataFrame:
    df = df.copy()
    closes = df["c"].to_numpy(dtype=float)
    kf = _kalman(closes, r)
    slope = np.empty_like(kf)
    slope[0] = 0.0
    slope[1:] = kf[1:] - kf[:-1]
    df["kf"] = kf
    df["kf_slope"] = slope
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
