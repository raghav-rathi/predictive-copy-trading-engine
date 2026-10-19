"""Bill Williams fractal breakout indicators.

5-bar fractals (``n``=2 bars each side):
  up fractal (resistance) at bar i if high[i] is strictly greater than
      the highs of bars i-n..i+n excluding i
  dn fractal (support)   at bar i if low[i] is strictly lower than
      the lows of bars i-n..i+n excluding i

A fractal is only CONFIRMED n bars later, so its level becomes visible
at bar i+n: ``up_level`` / ``dn_level`` are the last CONFIRMED fractal
high/low forward-filled (NaN until the first confirmation). This keeps
the confirmed-level series lookahead-free by construction.

Trend filter: SMA200 of close (documented substitute for the Alligator,
which the fractal source describes as the primary trend gate).

No lookahead: at bar j, up_level/dn_level only reflect fractals with
index <= j-n, whose computation needs data through (j-n)+n = j.

Source: https://arongroups.co/technical-analyze/bill-williams-indicators/
"""

import numpy as np
import pandas as pd

from strategies import base as B

FRACTAL_N = 2
SMA_N = 200


def _strict_extremes(h: np.ndarray, l: np.ndarray, n: int):
    """Boolean masks: up[i] (dn[i]) True when bar i is a strict local
    high (low) over the (2n+1)-bar window excluding i."""
    m = len(h)
    up = np.zeros(m, dtype=bool)
    dn = np.zeros(m, dtype=bool)
    for i in range(n, m - n):
        win_h = h[i - n : i + n + 1]
        win_l = l[i - n : i + n + 1]
        others_h = np.delete(win_h, n)
        others_l = np.delete(win_l, n)
        up[i] = bool(np.all(h[i] > others_h))
        dn[i] = bool(np.all(l[i] < others_l))
    return up, dn


def add_indicators(
    df: pd.DataFrame,
    n: int = FRACTAL_N,
    sma_n: int = SMA_N,
) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    up, dn = _strict_extremes(h, l, n)
    # confirmed n bars late: shift the level by n, then forward-fill
    df["up_level"] = pd.Series(np.where(up, h, np.nan), index=df.index).shift(n).ffill()
    df["dn_level"] = pd.Series(np.where(dn, l, np.nan), index=df.index).shift(n).ffill()
    df["up_fractal_bar"] = up
    df["dn_fractal_bar"] = dn
    df["sma200"] = B.sma(df["c"], sma_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
