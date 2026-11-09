"""Linear regression slope indicators.

OLS regression of close on bar index over the last PERIOD bars:
slope = sum((x - xbar)(y - ybar)) / sum((x - xbar)^2) with x = 0..19,
R^2 = slope^2 * Sxx / SStot (the fraction of the window's price
variance explained by the fitted line; 0 when the window is flat).
linreg_slope_norm = slope / close, so the slope is comparable across
coins priced orders of magnitude apart. linreg_value is the fitted
line's value at the current bar. All windows end at bar i, so no
lookahead.
"""

import numpy as np
import pandas as pd

PERIOD = 20

_X = np.arange(PERIOD, dtype=float) - (PERIOD - 1) / 2.0
_SXX = float((_X**2).sum())  # 665 for PERIOD == 20

INDICATOR_COLS = [
    "linreg_slope",
    "linreg_slope_norm",
    "linreg_r2",
    "linreg_value",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    slope = c.rolling(PERIOD, min_periods=PERIOD).apply(
        lambda a: float(np.dot(a - a.mean(), _X)) / _SXX, raw=True
    )
    ybar = c.rolling(PERIOD, min_periods=PERIOD).mean()
    # SS_tot = sum(y^2) - n * ybar^2 (per-window; the (c - ybar)^2 form
    # would wrongly pair each bar with its own trailing mean).
    ss_tot = (c**2).rolling(PERIOD, min_periods=PERIOD).sum() - PERIOD * ybar**2
    r2 = (slope**2 * _SXX / ss_tot).where(ss_tot > 0, 0.0).clip(0.0, 1.0)
    df["linreg_slope"] = slope
    df["linreg_slope_norm"] = slope / c
    df["linreg_r2"] = r2
    df["linreg_value"] = ybar + slope * (PERIOD - 1) / 2.0
    return df
