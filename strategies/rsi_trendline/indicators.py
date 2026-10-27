"""RSI(14) trendline breaks, causal.

Swing highs/lows of the RSI series are confirmed with a 3-bar window
(pivot at j is only used once bar j+3 has printed, so no lookahead:
every pivot admitted at bar i uses RSI data through bar i only).
The resistance line joins the last two confirmed swing highs; the
support line joins the last two confirmed swing lows. A long fires
when RSI crosses above a *descending* resistance line; a short when
it crosses below an *ascending* support line. Columns: rsi, rsi_line
(the active line value, NaN until two pivots exist), rsi_break (+1/-1
on the break bar), atr.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 3


def _confirmed_pivots(rsi: np.ndarray, confirm: int = CONFIRM):
    """[(idx, value, kind)] kind=+1 high / -1 low, confirmed pivots only."""
    n = len(rsi)
    raw = []
    for j in range(confirm, n - confirm):
        window = rsi[j - confirm : j + confirm + 1]
        if np.isnan(window).any():
            continue
        if rsi[j] >= window.max():
            raw.append((j, rsi[j], 1))
        if rsi[j] <= window.min():
            raw.append((j, rsi[j], -1))
    raw.sort(key=lambda p: p[0])
    out = []
    for j, px, kind in raw:
        if not out or kind != out[-1][2]:
            out.append((j, px, kind))
        else:
            pj, ppx, _ = out[-1]
            if (kind == 1 and px > ppx) or (kind == -1 and px < ppx):
                out[-1] = (j, px, kind)
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], 14).to_numpy(dtype=float)
    n = len(df)
    pivots = _confirmed_pivots(rsi)
    line = np.full(n, np.nan)
    brk = np.zeros(n, dtype=int)
    highs: list = []
    lows: list = []
    k = 0
    prev_above = False
    prev_below = False
    for i in range(n):
        while k < len(pivots) and pivots[k][0] <= i - CONFIRM:
            (highs if pivots[k][2] == 1 else lows).append(pivots[k])
            k += 1
        above = False
        below = False
        if len(highs) >= 2:
            (i1, v1, _), (i2, v2, _) = highs[-2], highs[-1]
            slope = (v2 - v1) / (i2 - i1) if i2 != i1 else 0.0
            if slope < 0:
                line[i] = v2 + slope * (i - i2)
                above = rsi[i] > line[i]
        if len(lows) >= 2:
            (i1, v1, _), (i2, v2, _) = lows[-2], lows[-1]
            slope = (v2 - v1) / (i2 - i1) if i2 != i1 else 0.0
            if slope > 0:
                lv = v2 + slope * (i - i2)
                if np.isnan(line[i]):
                    line[i] = lv
                below = rsi[i] < lv
        if above and not prev_above:
            brk[i] = 1
        elif below and not prev_below:
            brk[i] = -1
        prev_above, prev_below = above, below
    df["rsi"] = rsi
    df["rsi_line"] = line
    df["rsi_break"] = brk
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
