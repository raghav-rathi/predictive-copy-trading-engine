"""Rising / falling wedge breakout on zigzag pivots.

A wedge is two converging trendlines: a rising wedge has higher highs
and higher lows with the highs rising slower than the lows (the lines
converge upward) and breaks down; a falling wedge has lower highs and
lower lows with the highs falling faster (converging downward) and
breaks up. Trendlines are fit through the last two swing highs and
the last two swing lows — no regression, no fitted parameters beyond
the pivot window.

Columns:
    wedge_dir   -- -1 rising wedge pending, +1 falling wedge, else 0
    wedge_level -- breakout trendline value at bar i (lower line for
                   rising wedges, upper line for falling wedges)
    atr         -- Wilder ATR(14) for the risk layer

Pending state is sticky until price breaks out the wrong way (rising
wedge breaking up, falling wedge breaking down clears it). The
trendline level moves with bar i (extrapolated slope), so the entry
level is whatever the line says on the entry bar. No lookahead: same
causal 5-bar zigzag confirmation as abcd_pattern.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CONFIRM = 5
MAX_SPAN = 80  # all four pivots must be within the last 80 bars


def _slope(p1, p2):
    return (p2[1] - p1[1]) / (p2[0] - p1[0]) if p2[0] != p1[0] else 0.0


def add_indicators(df: pd.DataFrame, confirm: int = CONFIRM) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    confirmed: list[tuple[int, float, int]] = []
    pending_dir = 0
    pending_level = float("nan")
    pending_invalid = float("nan")

    dir_col = np.zeros(n, dtype=int)
    level_col = np.full(n, np.nan)

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

        if pending_dir == 0:
            highs = [p for p in confirmed if p[2] == 1][-2:]
            lows = [p for p in confirmed if p[2] == -1][-2:]
            if len(highs) == 2 and len(lows) == 2:
                h1, h2 = highs
                l1, l2 = lows
                if i - h1[0] <= MAX_SPAN and i - l1[0] <= MAX_SPAN:
                    hs = _slope(h1, h2)
                    ls = _slope(l1, l2)
                    if hs > 0 and ls > 0 and hs < ls:
                        # rising wedge: converges upward, breaks down
                        pending_dir = -1
                        pending_level = l2[1] + ls * (i - l2[0])
                        pending_invalid = h2[1] + hs * (i - h2[0])
                    elif hs < 0 and ls < 0 and hs < ls:
                        # falling wedge: highs fall faster, converges down
                        pending_dir = 1
                        pending_level = h2[1] + hs * (i - h2[0])
                        pending_invalid = l2[1] + ls * (i - l2[0])
        else:
            # keep the extrapolated level current while pending
            highs = [p for p in confirmed if p[2] == 1][-2:]
            lows = [p for p in confirmed if p[2] == -1][-2:]
            if len(highs) == 2 and len(lows) == 2:
                h1, h2 = highs
                l1, l2 = lows
                hs = _slope(h1, h2)
                ls = _slope(l1, l2)
                if pending_dir == -1:
                    pending_level = l2[1] + ls * (i - l2[0])
                    pending_invalid = h2[1] + hs * (i - h2[0])
                    if c[i] > pending_invalid:
                        pending_dir = 0
                        pending_level = float("nan")
                        pending_invalid = float("nan")
                else:
                    pending_level = h2[1] + hs * (i - h2[0])
                    pending_invalid = l2[1] + ls * (i - l2[0])
                    if c[i] < pending_invalid:
                        pending_dir = 0
                        pending_level = float("nan")
                        pending_invalid = float("nan")

        dir_col[i] = pending_dir
        level_col[i] = pending_level

    df["wedge_dir"] = dir_col
    df["wedge_level"] = level_col
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
