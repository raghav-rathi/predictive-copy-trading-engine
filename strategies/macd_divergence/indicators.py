"""MACD histogram divergence on zigzag price pivots (causal).

The Aspray MACD-Histogram divergence: price makes a lower low while
the histogram makes a higher low (bullish), or price makes a higher
high while the histogram makes a lower high (bearish). Divergence is
detected when the second price pivot confirms (5-bar lag), and it
fires exactly once per pivot pair — the same fire-once discipline as
abcd_pattern.

Columns:
    macd      -- EMA(12) - EMA(26) of close
    macd_sig  -- EMA(9) of macd
    macd_hist -- macd - macd_sig
    macd_div_dir -- +1 on a bullish divergence bar, -1 bearish, else 0
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: EMAs are causal, and the pivot confirmation lag means a
divergence bar only ever reads histogram values at already-confirmed
pivot bars.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
FAST = 12
SLOW = 26
SIGNAL = 9


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)

    macd = B.ema(df["c"], FAST) - B.ema(df["c"], SLOW)
    sig = B.ema(macd, SIGNAL)
    hist = (macd - sig).to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []  # (idx, price, kind)
    div_col = np.zeros(n, dtype=int)
    last_fired_pivot = -1

    for i in range(n):
        j = i - confirm
        if j >= confirm:
            if h[j] >= h[j - confirm:j + confirm + 1].max():
                piv = (j, h[j], 1)
                if confirmed and confirmed[-1][2] == 1:
                    if piv[1] > confirmed[-1][1]:
                        confirmed[-1] = piv
                else:
                    confirmed.append(piv)
            if l[j] <= l[j - confirm:j + confirm + 1].min():
                piv = (j, l[j], -1)
                if confirmed and confirmed[-1][2] == -1:
                    if piv[1] < confirmed[-1][1]:
                        confirmed[-1] = piv
                else:
                    confirmed.append(piv)
        if len(confirmed) >= 3 and confirmed[-1][0] != last_fired_pivot:
            # last two pivots of the newest pivot's kind, with one pivot between
            kind = confirmed[-1][2]
            same = [p for p in confirmed if p[2] == kind][-2:]
            if len(same) == 2:
                p1, p2 = same
                h1, h2 = hist[p1[0]], hist[p2[0]]
                if np.isfinite(h1) and np.isfinite(h2):
                    if kind == -1 and p2[1] < p1[1] and h2 > h1:
                        div_col[i] = 1
                        last_fired_pivot = confirmed[-1][0]
                    elif kind == 1 and p2[1] > p1[1] and h2 < h1:
                        div_col[i] = -1
                        last_fired_pivot = confirmed[-1][0]

    df["macd"] = macd
    df["macd_sig"] = sig
    df["macd_hist"] = hist
    df["macd_div_dir"] = div_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
