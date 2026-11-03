"""Blau Double Smoothed Stochastic indicators.

William Blau Double Smoothed Stochastic (21, 3, 3): stochastic %K double-smoothed with EMAs and traded against its 3-bar EMA trigger. Long on DSS cross above trigger, short on cross below; exits on the opposite cross.
"""

import pandas as pd

from strategies import base as B

PERIOD = 21


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(PERIOD, min_periods=PERIOD).max()
    ll = df["l"].rolling(PERIOD, min_periods=PERIOD).min()
    rng = (hh - ll).replace(0, float("nan"))
    raw = (df["c"] - ll) / rng * 100.0
    dss = raw.ewm(span=3, adjust=False, min_periods=3).mean().ewm(span=3, adjust=False, min_periods=3).mean()
    df["dss"] = dss
    df["dss_trigger"] = dss.ewm(span=3, adjust=False, min_periods=3).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
