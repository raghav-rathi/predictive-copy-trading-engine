"""Schaff Trend Cycle (Doug Schaff) indicators.

Construction (per the task spec):
  macd_line = EMA(c,12) - EMA(c,26)
  stoch = 100 * (macd_line - min50(macd_line)) / (max50 - min50)
  k  = EMA(stoch, 23)
  d  = EMA(k, 50)
  stc = clip(EMA(d, 10), 0, 100)

Signals consume stc_s (STC shifted by 1, i.e. the value formed at the
current bar's close, not including any later information) so there is no
lookahead. The raw "stc" column is kept for debugging; signals use "stc_s".
EMA chain: B.ema already carries min_periods; nested EMAs need the sum of
lookbacks before going non-NaN (~150 bars here).
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    macd_line = B.ema(df["c"], 12) - B.ema(df["c"], 26)
    lo50 = macd_line.rolling(50, min_periods=50).min()
    hi50 = macd_line.rolling(50, min_periods=50).max()
    rng = (hi50 - lo50).replace(0, float("nan"))
    stoch = 100 * (macd_line - lo50) / rng
    k = B.ema(stoch, 23)
    d = B.ema(k, 50)
    stc_raw = B.ema(d, 10)
    df["stc"] = stc_raw.clip(0, 100)
    # formed with the current bar: usable on the next bar, no lookahead
    df["stc_s"] = df["stc"].shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
