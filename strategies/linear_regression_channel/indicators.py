"""Raff regression channel, mean-reversion form.

Over each trailing N=50-bar window, fit OLS of closes against the
bar index within the window (closed form via rolling sums, exactly
equivalent to np.polyfit on the window). The fitted value at the
current bar is the channel midline; resid_std is the population
standard deviation of (closes - fitted) over the window; the bands
are mid +/- 2*resid_std.

The closed-form derivation: with x = 0..N-1 in-window, mean_x and
Sxx are constants; slope = (sum(x*y) - mean_x*sum(y)) / Sxx and
mid = mean_y + slope*(N-1-mean_x). Residual sum of squares uses
the OLS identity SSR = sum(y^2) - a*sum(y) - b*sum(x*y), clipped
at zero for floating-point safety. Every window uses only closes
up to and including the current bar, so the channel is causal.

Columns:
    lr_mid, lr_upper, lr_lower -- channel lines (NaN before 50 bars)
    lr_slope                   -- fitted slope per bar
    lr_std                     -- residual std per bar
    atr                        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 50
K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(c)
    x = np.arange(N, dtype=float)
    mean_x = x.mean()
    sxx = float(((x - mean_x) ** 2).sum())
    sum_x = float(x.sum())

    y = pd.Series(c)
    roll_y = y.rolling(N, min_periods=N).sum().to_numpy(dtype=float)
    roll_y2 = (y * y).rolling(N, min_periods=N).sum().to_numpy(dtype=float)
    # sum of j*y_j over the window, j = absolute bar index; convert
    # to in-window x*y by subtracting start*sum(y).
    jy = pd.Series(np.arange(n, dtype=float) * c)
    roll_jy = jy.rolling(N, min_periods=N).sum().to_numpy(dtype=float)
    start = np.arange(n, dtype=float) - (N - 1)
    roll_xy = roll_jy - start * roll_y

    mean_y = roll_y / N
    slope = (roll_xy - mean_x * roll_y) / sxx
    intercept = mean_y - slope * mean_x
    mid = mean_y + slope * (N - 1 - mean_x)
    ssr = roll_y2 - intercept * roll_y - slope * roll_xy
    ssr = np.where(np.isfinite(ssr), np.maximum(ssr, 0.0), np.nan)
    resid_std = np.sqrt(ssr / N)

    df["lr_mid"] = mid
    df["lr_upper"] = mid + K * resid_std
    df["lr_lower"] = mid - K * resid_std
    df["lr_slope"] = slope
    df["lr_std"] = resid_std
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
