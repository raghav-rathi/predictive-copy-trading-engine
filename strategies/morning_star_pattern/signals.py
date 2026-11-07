"""Morning/Evening Star signals.

Enter long on a completed morning star, short on a completed evening
star (the harness executes at the next bar's open). Exit a long on the
opposite (evening star) pattern, a short on a morning star; the ATR
stop / trail from the risk layer also applies.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    morning = df["ms_morning"] > 0
    evening = df["ms_evening"] > 0
    df["long_entry"] = morning.astype(bool)
    df["short_entry"] = evening.astype(bool)
    df["long_exit"] = evening.astype(bool)
    df["short_exit"] = morning.astype(bool)
    return df
