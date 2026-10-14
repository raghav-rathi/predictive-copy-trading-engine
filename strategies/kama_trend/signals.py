"""KAMA trend signals.

Entry: close crosses KAMA while the efficiency ratio is above 0.3, i.e.
the cross happens in a genuinely trending market, not in chop.
    long_entry  = cross(close above kama) AND ER > 0.3
    short_entry = cross(close below kama) AND ER > 0.3
Exit: the mirror cross (no ER filter on exits -- get out when the trend
breaks regardless of efficiency).
    long_exit   = cross(close below kama)
    short_exit  = cross(close above kama)
Risk-level exits (stop) come from risk.py.
"""

import pandas as pd

from strategies import base as B
from strategies.kama_trend import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = B.crossed_above(df["c"], df["kama"])
    dn = B.crossed_below(df["c"], df["kama"])
    trending = df["er"] > I.ER_MIN
    df["long_entry"] = (up & trending).fillna(False)
    df["short_entry"] = (dn & trending).fillna(False)
    df["long_exit"] = dn.fillna(False)
    df["short_exit"] = up.fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
