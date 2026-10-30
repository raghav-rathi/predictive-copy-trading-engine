"""VWAP standard-deviation bands indicators (causal, no lookahead).

UTC-day session VWAP: typical price * volume cumulated from
the UTC midnight boundary, divided by cumulated volume
(crypto trades 24/7, so the session is the UTC calendar day).
Bands at VWAP +/- 1 sigma and +/- 2 sigma, where sigma is
the practical proxy specified for this strategy: the 20-bar
rolling standard deviation of (close - VWAP). The rolling
window is trailing, so for the first bars of a UTC day it
may straddle the midnight boundary; the band itself always
resets with the day's VWAP. Sigma uses min_periods=2 and a
0 fill for the single first bar, so the band columns contain
no NaN at all.

Columns:
    vwap, vwap_sigma, vwap_upper_1, vwap_lower_1,
    vwap_upper_2, vwap_lower_2, atr
"""

import numpy as np
import pandas as pd

from strategies import base as B

SIGMA_BARS = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = pd.to_datetime(df["t"], unit="ms", utc=True)
    day = t.dt.floor("D").to_numpy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    cum_pv = (tp * df["v"]).groupby(day).cumsum()
    cum_v = df["v"].groupby(day).cumsum()
    vwap = cum_pv / cum_v.replace(0, np.nan)
    vwap = vwap.fillna(tp)
    df["vwap"] = vwap
    diff = df["c"] - vwap
    sigma = diff.rolling(SIGMA_BARS, min_periods=2).std().fillna(0.0)
    df["vwap_sigma"] = sigma
    df["vwap_upper_1"] = vwap + sigma
    df["vwap_lower_1"] = vwap - sigma
    df["vwap_upper_2"] = vwap + 2 * sigma
    df["vwap_lower_2"] = vwap - 2 * sigma
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
