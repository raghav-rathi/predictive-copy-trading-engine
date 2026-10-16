"""Key-reversal bar indicators (classic floor-trader pattern),
implemented in my own words.

Bearish key reversal on bar i:
  h[i] == max(h[i-19..i])      (a new 20-bar high)
  AND c[i] < l[i-1]            (closes below the prior bar's low)

Bullish key reversal on bar i:
  l[i] == min(l[i-19..i])      (a new 20-bar low)
  AND c[i] > h[i-1]            (closes above the prior bar's high)

Volume confirmation: v[i] > 1.5 * SMA(v, 20). The signals module can
run with or without the volume filter (USE_VOLUME_FILTER); calibration
compares both and the winner ships as default.
"""

import pandas as pd

LOOKBACK = 20
VOL_MULT = 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h, l, c, v = df["h"], df["l"], df["c"], df["v"]
    hi = h.rolling(LOOKBACK, min_periods=LOOKBACK).max()
    lo = l.rolling(LOOKBACK, min_periods=LOOKBACK).min()
    vol_sma = v.rolling(LOOKBACK, min_periods=LOOKBACK).mean()

    df["kr_bear"] = ((h == hi) & (c < l.shift(1))).fillna(False)
    df["kr_bull"] = ((l == lo) & (c > h.shift(1))).fillna(False)
    df["kr_vol_conf"] = (v > VOL_MULT * vol_sma).fillna(False)
    return df
