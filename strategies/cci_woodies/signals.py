"""Woodies CCI signals: zero-line crosses after a hook from the extreme.

long_entry  = CCI crosses above 0  AND  CCI printed below -100 within the
              last 20 bars (the hook)
short_entry = CCI crosses below 0  AND  CCI printed above +100 within the
              last 20 bars
long_exit   = CCI crosses back below 0
short_exit  = CCI crosses back above 0
Execution next-bar-open per the harness contract.
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.cci_woodies import indicators as ind


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cci = df["cci"]
    zero = pd.Series(np.zeros(len(df)), index=df.index)
    hook_down = df["cci_min20"] < -ind.HOOK
    hook_up = df["cci_max20"] > ind.HOOK
    df["long_entry"] = B.crossed_above(cci, zero) & hook_down
    df["short_entry"] = B.crossed_below(cci, zero) & hook_up
    df["long_exit"] = B.crossed_below(cci, zero)
    df["short_exit"] = B.crossed_above(cci, zero)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
