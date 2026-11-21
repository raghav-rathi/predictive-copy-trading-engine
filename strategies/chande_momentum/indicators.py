"""Chande Momentum Oscillator indicators.

Tushar Chande, "The New Technical Trader" (1994). Over a trailing
window of N = 14 bars:

    up_t   = max(c_t - c_{t-1}, 0)
    down_t = max(c_{t-1} - c_t, 0)
    Su     = sum of up over the trailing 14 bars
    Sd     = sum of down over the trailing 14 bars
    CMO    = 100 * (Su - Sd) / (Su + Sd)

The oscillator ranges from -100 to +100. A zero denominator (all
closes flat over the window) is guarded to CMO = 0. The +50 / -50
levels are Chande's conventional overbought / oversold thresholds.

Columns:
    cmo -- Chande Momentum Oscillator (14)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only. Rolling sums are trailing (include bar i, exclude later bars).
"""

import numpy as np
import pandas as pd

from strategies import base as B

CMO_N = 14
ATR_N = 14


def add_indicators(df: pd.DataFrame, cmo_n: int = CMO_N,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    h = df["h"]
    l = df["l"]

    delta = c.diff()
    up = delta.clip(lower=0)
    down = (-delta).clip(lower=0)
    su = up.rolling(cmo_n, min_periods=cmo_n).sum()
    sd = down.rolling(cmo_n, min_periods=cmo_n).sum()
    denom = su + sd
    cmo = 100.0 * (su - sd) / denom.replace(0, np.nan)
    df["cmo"] = cmo.fillna(0.0).where(denom.notna() & (denom != 0), np.nan)
    # Flat window (Su = Sd = 0, denominator 0) -> CMO 0 once defined;
    # NaN while the window is not yet full.
    df["cmo"] = np.where(
        denom.notna() & (denom == 0), 0.0, df["cmo"].to_numpy(dtype=float)
    )
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
