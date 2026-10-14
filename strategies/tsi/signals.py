"""TSI signals (Blau).

Long  on TSI crossing above its signal line; short on the cross below.
zero_gate (default on): entries only fire when momentum is on the
mean-reverting side at the cross (TSI < 0 for longs, TSI > 0 for shorts).
exhaustion (default off): Blau's +/-25 exhaustion levels act as extra
exits. Opposite cross always exits.
"""

import pandas as pd

from strategies import base as B

EXHAUST_LEVEL = 25.0


def add_signals(
    df: pd.DataFrame, zero_gate: bool = True, exhaustion: bool = False
) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["tsi"], df["tsi_signal"]).fillna(False)
    cross_dn = B.crossed_below(df["tsi"], df["tsi_signal"]).fillna(False)
    if zero_gate:
        long_ok = df["tsi"] < 0
        short_ok = df["tsi"] > 0
    else:
        long_ok = True
        short_ok = True
    df["long_entry"] = cross_up & long_ok
    df["short_entry"] = cross_dn & short_ok
    if exhaustion:
        df["long_exit"] = cross_dn | (df["tsi"] >= EXHAUST_LEVEL)
        df["short_exit"] = cross_up | (df["tsi"] <= -EXHAUST_LEVEL)
    else:
        df["long_exit"] = cross_dn
        df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
