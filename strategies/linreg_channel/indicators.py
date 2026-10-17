"""Linear-regression channel indicators (Gilbert Raff).

LSMA(n) = the end-point of the least-squares line fit to the last n
closes. Channel = LSMA +/- K * std(residuals) over the same window.
Tags: low touches the lower band and closes back above it (rejection),
high touches the upper band and closes back below it. All causal:
the fit at bar i uses only closes through i.
"""

import numpy as np
import pandas as pd

N = 50
K = 2.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy()
    n = len(df)
    lsma = np.full(n, np.nan)
    sd = np.full(n, np.nan)
    x = np.arange(N, dtype=float)
    x = x - x.mean()
    denom = (x ** 2).sum()
    for i in range(N - 1, n):
        w = c[i - N + 1 : i + 1]
        y = w - w.mean()
        slope = (x * y).sum() / denom
        fit_end = w.mean() + slope * (x[-1])
        resid = w - (w.mean() + slope * x)
        lsma[i] = fit_end
        sd[i] = resid.std(ddof=1)
    upper = lsma + K * sd
    lower = lsma - K * sd
    df["lr_lsma"] = lsma
    df["lr_upper"] = upper
    df["lr_lower"] = lower
    # tag = low touched the band intrabar (wick) but close held inside
    df["tag_low"] = (df["l"] <= lower) & (df["c"] > lower)
    df["tag_high"] = (df["h"] >= upper) & (df["c"] < upper)
    return df
