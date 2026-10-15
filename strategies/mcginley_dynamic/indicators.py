"""McGinley Dynamic indicators (John McGinley, 1990).

MD[i] = MD[i-1] + (price[i] - MD[i-1]) / (N * (price[i] / MD[i-1])^4)

The ^4 term makes the line accelerate toward price in fast (bear)
moves and lag less in slow (bull) moves — an automatic market-speed
adjustment no fixed-period MA has. The traded system is the fast/slow
Dynamic cross. No lookahead: purely recursive on bars through i.
"""

import numpy as np
import pandas as pd

FAST_N = 10
SLOW_N = 30


def _mcginley(values: np.ndarray, n: int) -> np.ndarray:
    out = np.empty(len(values))
    md = values[0]
    out[0] = md
    for i in range(1, len(values)):
        px = values[i]
        # prices are positive; md tracks price so the ratio stays sane
        ratio = px / md if md != 0 else 1.0
        md = md + (px - md) / (n * ratio**4)
        out[i] = md
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    df["md_fast"] = _mcginley(c, FAST_N)
    df["md_slow"] = _mcginley(c, SLOW_N)
    return df
