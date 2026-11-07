"""Floor-trader pivot signals.

Bias: close above PP = long-only, close below PP = short-only.
Long: close above R1 with volume above its 20-bar average -> enter;
exit at R2 (close >= R2) or on a close back below PP. Short: close
below S1 with volume above average -> enter; exit at S2 (close <= S2)
or on a close back above PP. All levels are computed from the trailing
24 completed bars, so signals on bar i use only data through bar i's
close (levels themselves use data through bar i-1).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    v = df["v"]
    pp = df["fp_pp"]
    r1 = df["fp_r1"]
    s1 = df["fp_s1"]
    r2 = df["fp_r2"]
    s2 = df["fp_s2"]
    vol_avg = df["fp_vol_avg"]
    vol_ok = (v > vol_avg).fillna(False)
    df["long_entry"] = ((c > pp) & (c > r1) & vol_ok).fillna(False).astype(bool)
    df["short_entry"] = ((c < pp) & (c < s1) & vol_ok).fillna(False).astype(bool)
    df["long_exit"] = ((c >= r2) | (c < pp)).fillna(False).astype(bool)
    df["short_exit"] = ((c <= s2) | (c > pp)).fillna(False).astype(bool)
    return df
