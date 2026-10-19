"""Chande Forecast Oscillator indicators.

TSF: the n=20 linear-regression (time series forecast) of close. For each
bar i >= n, an OLS line is fit on the trailing window closes[i-n..i-1]
and extrapolated one step ahead -> the forecast made at bar i-1 for
bar i (no lookahead).

FO (forecast oscillator) = (close_i - forecast_{i-1->i}) / close_i * 100.
signal = 3-bar SMA of FO.

The vectorized form precomputes the OLS projection weights once and
applies them to every trailing window: exactly np.polyfit(x, y, 1)
extrapolated to x = n for each window.
"""

import numpy as np
import pandas as pd

from strategies import base as B

TSF_N = 20
SIGNAL_N = 3


def _one_step_forecast(y: np.ndarray, n: int = TSF_N) -> np.ndarray:
    """Forecast made at bar i-1 for bar i via OLS on trailing n closes.
    out[i] is NaN for i < n."""
    m = len(y)
    X = np.column_stack([np.ones(n), np.arange(n, dtype=float)])
    proj = np.linalg.inv(X.T @ X) @ X.T          # 2 x n
    weights = np.array([1.0, float(n)]) @ proj   # n weights on the window
    windows = np.lib.stride_tricks.sliding_window_view(y, n)
    pred = windows @ weights       # pred[k] -> forecast for bar k+n
    out = np.full(m, np.nan)
    out[n:] = pred[: m - n]         # drop pred[m-n]: forecast for bar m (nonexistent)
    return out


def add_indicators(
    df: pd.DataFrame,
    tsf_n: int = TSF_N,
    signal_n: int = SIGNAL_N,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    tsf_prev = _one_step_forecast(c, tsf_n)
    with np.errstate(divide="ignore", invalid="ignore"):
        fo = (c - tsf_prev) / np.where(c == 0.0, np.nan, c) * 100.0
    df["tsf_prev"] = tsf_prev
    df["fo"] = fo
    df["fo_signal"] = B.sma(pd.Series(fo, index=df.index), signal_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
