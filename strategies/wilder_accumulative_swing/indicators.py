"""J. Welles Wilder Accumulative Swing Index (ASI) indicators.

Per bar i >= 1 (C/O = current close/open, Cy/Oy = prior close/open):
    numerator = (C - Cy) + 0.5 * (C - O) + 0.25 * (Cy - Oy)
    R         = max(H - Cy, Cy - L, H - L)
    SI        = 50 * numerator / R, with SI = 0 when R == 0
    ASI       = cumulative sum of SI, with ASI = 0 on the first bar
                (SI starts at bar 1; bar 0 has no prior bar)
    asi_ema   = EMA(ASI, 10) via strategies.base ema

R variant note: this implementation uses R = max(H - Cy, Cy - L, H - L)
exactly as specified for this strategy. It is always positive when
H > L (since H - L > 0 is one of the candidates); the R == 0 guard
covers only the degenerate flat bar H == L (where all three candidates
are 0). All inputs use only bars up to and including the current bar
(prior-bar values via shift), so the computation is strictly causal.

Columns:
    si, asi, asi_ema -- swing index, accumulative swing index, EMA(10) of ASI
    atr              -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_PERIOD = 10


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, o, h, l = df["c"], df["o"], df["h"], df["l"]
    cy, oy = c.shift(1), o.shift(1)
    numerator = (c - cy) + 0.5 * (c - o) + 0.25 * (cy - oy)
    r = pd.concat([h - cy, cy - l, h - l], axis=1).max(axis=1)
    si = np.where((r != 0) & r.notna(), 50.0 * numerator / r.replace(0, np.nan), 0.0)
    df["si"] = pd.Series(si, index=df.index).fillna(0.0)
    df["asi"] = df["si"].cumsum()
    df["asi_ema"] = B.ema(df["asi"], EMA_PERIOD)
    df["atr"] = B.atr(h, l, c, 14)
    return df
