"""Hull MA trend signals.

Design note: HMA's low lag means price crosses the HMA *before* its slope
turns on a V-reversal, so a strict "cross while rising" AND-rule almost
never fires. The implementable classic is the slope turn with price
confirmation:

long_entry  = HMA slope crosses above 0 with close above the HMA
short_entry = HMA slope crosses below 0 with close below the HMA
long_exit   = HMA slope crosses below 0  OR  close crosses below the HMA
short_exit  = HMA slope crosses above 0  OR  close crosses above the HMA
Execution next-bar-open per the harness contract.
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, hma, slope = df["c"], df["hma"], df["hma_slope"]
    zero = pd.Series(np.zeros(len(df)), index=df.index)
    slope_up = B.crossed_above(slope, zero)
    slope_dn = B.crossed_below(slope, zero)
    long_x = B.crossed_above(c, hma)
    short_x = B.crossed_below(c, hma)
    df["long_entry"] = slope_up & (c > hma)
    df["short_entry"] = slope_dn & (c < hma)
    df["long_exit"] = slope_dn | short_x
    df["short_exit"] = slope_up | long_x
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
