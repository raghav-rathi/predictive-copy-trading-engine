"""Time-series momentum signals (Liu & Tsyvinski-style).

Long  when both the 1-week (r168_s) and 4-week (r672_s) vol-scaled returns
      cross above +0.5
Short when both cross below -0.5
Exit long  when both ratios decay below +0.3 (hysteresis)
Exit short when both ratios decay above -0.3 (hysteresis)

The cross is implemented manually as (r > k) & (r.shift(1) <= k) because
base.crossed_above broadcasts a scalar b but then calls b.shift(1),
which fails on a plain float.
"""

import pandas as pd

ENTRY_K = 0.5
EXIT_K = 0.3


def _crossed_above(r: pd.Series, k: float) -> pd.Series:
    return (r > k) & (r.shift(1) <= k)


def _crossed_below(r: pd.Series, k: float) -> pd.Series:
    return (r < -k) & (r.shift(1) >= -k)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    r1 = df["r168_s"]
    r2 = df["r672_s"]
    df["long_entry"] = _crossed_above(r1, ENTRY_K) & _crossed_above(r2, ENTRY_K)
    df["short_entry"] = _crossed_below(r1, ENTRY_K) & _crossed_below(r2, ENTRY_K)
    df["long_exit"] = (r1 < EXIT_K) & (r2 < EXIT_K)
    df["short_exit"] = (r1 > -EXIT_K) & (r2 > -EXIT_K)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
