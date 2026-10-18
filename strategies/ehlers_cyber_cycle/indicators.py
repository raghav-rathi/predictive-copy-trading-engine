"""John Ehlers' Cyber Cycle indicators ("Cybernetic Analysis for Stocks
and Futures").

smooth_i = (h_i + l_i) / 2, then with alpha = 0.07:

  cycle_i = (1-a/2)^2 * (smooth_i - 2*smooth_{i-1} + smooth_{i-2})
          + 2*(1-a) * cycle_{i-1} - (1-a)^2 * cycle_{i-2}

The recursion is seeded with 0 for out-of-range terms (no lookahead:
every value on bar i uses bars through i only).  trigger = cycle
lagged 1 bar.  Entries on cycle crossing the trigger; the cycle is a
high-pass-filtered second-difference, so the cross is a turning-point
detector of the dominant cycle.

No lookahead: pure causal recursion.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ALPHA = 0.07


def add_indicators(df: pd.DataFrame, alpha: float = ALPHA) -> pd.DataFrame:
    df = df.copy()
    hv = df["h"].to_numpy()
    lv = df["l"].to_numpy()
    n = len(df)
    smooth = (hv + lv) / 2.0
    k1 = (1.0 - alpha / 2.0) ** 2
    k2 = 2.0 * (1.0 - alpha)
    k3 = (1.0 - alpha) ** 2
    cycle = np.zeros(n)
    for i in range(n):
        sm = smooth[i]
        sm1 = smooth[i - 1] if i >= 1 else 0.0
        sm2 = smooth[i - 2] if i >= 2 else 0.0
        cy1 = cycle[i - 1] if i >= 1 else 0.0
        cy2 = cycle[i - 2] if i >= 2 else 0.0
        cycle[i] = k1 * (sm - 2.0 * sm1 + sm2) + k2 * cy1 - k3 * cy2
    df["cyber_cycle"] = cycle
    df["cyber_trigger"] = pd.Series(cycle, index=df.index).shift(1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
