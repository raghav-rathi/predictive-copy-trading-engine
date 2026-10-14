"""Tushar Chande's Chande Momentum Oscillator (CMO) indicators.

CMO = 100 * (Su - Sd) / (Su + Sd), where Su/Sd are the sums of up-day
and down-day closes over n bars. Unlike RSI (which smooths the ratio of
averages), CMO uses the raw sums, so it is more sensitive to short-term
momentum bursts. Range is symmetric: -100..+100, with +/-50 the classic
overbought/oversold marks. All causal: only data through bar i's close.
"""

import pandas as pd

N = 14  # Chande's standard CMO window


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["c"].diff()
    up = d.clip(lower=0.0)
    dn = -d.clip(upper=0.0)
    su = up.rolling(N, min_periods=N).sum()
    sd = dn.rolling(N, min_periods=N).sum()
    denom = (su + sd).replace(0, float("nan"))
    df["cmo"] = (100.0 * (su - sd) / denom).fillna(0.0)
    return df
