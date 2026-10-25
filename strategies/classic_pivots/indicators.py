"""Classic floor-trader pivot points, computed from the prior bar.

The original pivot formula (pre-dating Camarilla and Woodie variants,
both already in the library): from the previous bar's high, low and
close,

    PP = (H + L + C) / 3
    R1 = 2*PP - L
    S1 = 2*PP - H

Traded here as a breakout system: long when the close breaks above
R1, short when it breaks below S1, exit when the close falls back
through PP. On 1h bars the "prior period" is the prior bar, which
keeps the levels fresh every hour instead of freezing them for a
whole day.

Columns:
    piv_pp, piv_r1, piv_s1 -- levels from the previous bar
    atr                    -- Wilder ATR(14) for the risk layer

No lookahead: every level uses only bars <= i-1.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ph = df["h"].shift(1)
    pl = df["l"].shift(1)
    pc = df["c"].shift(1)
    pp = (ph + pl + pc) / 3.0
    df["piv_pp"] = pp
    df["piv_r1"] = 2.0 * pp - pl
    df["piv_s1"] = 2.0 * pp - ph
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
