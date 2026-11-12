"""Linear regression channel indicators.

OLS regression of close on the bar index over the last 100 bars.
Computed vectorized from rolling sums in centered form (window-local
x = 0..99, xbar = 49.5), which keeps the slope and residual variance
numerically stable — no cancellation against the global bar index:

    sxx    = sum (x - xbar)^2 = n (n^2 - 1) / 12  (constant per window)
    slope  = sum (x - xbar)(y - ybar) / sxx
    reg_mid = ybar + slope * (n - 1 - xbar)  (line value at bar i)
    RSS    = sum (y - ybar)^2 - slope^2 * sxx
    reg_std = sqrt(RSS / (n - 1))            (ddof=1, as in pandas std)
    reg_upper = reg_mid + 2.0 * reg_std
    reg_lower = reg_mid - 2.0 * reg_std
    atr      -- Wilder ATR(14) for the risk layer

The residuals are measured against the line fitted on the SAME 100
bars (the window ending at bar i), so the band width is defined as
soon as the window is full — bar 99 — with no extra lag.

No lookahead: every column on bar i uses only bars i-99..i (data
through bar i's close).
"""

import numpy as np
import pandas as pd

from strategies import base as B

REG_N = 100
BAND_K = 2.0

INDICATOR_COLS = ["reg_mid", "reg_upper", "reg_lower", "reg_slope",
                  "reg_std", "atr"]


def add_indicators(df: pd.DataFrame, n: int = REG_N,
                   k: float = BAND_K) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    t = pd.Series(np.arange(len(df), dtype=float), index=df.index)
    xbar = (n - 1) / 2.0
    sxx = n * (n * n - 1) / 12.0
    sum_y = c.rolling(n, min_periods=n).sum()
    sum_y2 = (c * c).rolling(n, min_periods=n).sum()
    sum_ty = (t * c).rolling(n, min_periods=n).sum()
    # Window-local x = t - (t_i - (n - 1)), so sum(x*y) over the
    # window is sum(t*y) - (t_i - (n - 1)) * sum(y).
    sum_xy = sum_ty - (t - (n - 1)) * sum_y
    sxy = sum_xy - xbar * sum_y
    slope = sxy / sxx
    mean_y = sum_y / n
    ss_tot = sum_y2 - sum_y * sum_y / n
    rss = ss_tot - slope * slope * sxx
    reg_std = np.sqrt((rss / (n - 1)).clip(lower=0))
    df["reg_slope"] = slope
    df["reg_mid"] = mean_y + slope * (n - 1 - xbar)
    df["reg_std"] = reg_std
    df["reg_upper"] = df["reg_mid"] + k * reg_std
    df["reg_lower"] = df["reg_mid"] - k * reg_std
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
