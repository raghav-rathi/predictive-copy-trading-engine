"""Funding Squeeze Reversal signals.

SHORT (fade crowded longs): 8h cumulative funding > +0.030% AND
    volume > 1.5x its 20-bar SMA AND weighted confidence >= 0.45.
LONG (fade crowded shorts): 8h cumulative funding < -0.020% AND
    volume > 1.5x its 20-bar SMA AND weighted confidence >= 0.45.
Skip any entry when volume > 3x its 20-bar SMA (violent spike guard).
Reversing exits: the opposite-side signal closes the position
(long_exit == short_entry, short_exit == long_entry). The hard stop /
chandelier trailing / 12-bar max hold live in risk.py and are enforced
by the harness. Execution is next-bar-open per the harness contract.
"""

import pandas as pd

from strategies.funding_squeeze_reversal import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["fund8"].notna() & df["vol_ratio"].notna() & df["fsr_conf"].notna()
    hot = df["vol_ratio"] > I.VOL_MIN_RATIO
    violent = df["vol_ratio"] > I.VOL_MAX_RATIO
    conf_ok = df["fsr_conf"] >= I.CONF_MIN
    df["short_entry"] = (
        (df["fund8"] > I.FUND_SHORT_THR) & hot & ~violent & conf_ok & valid
    )
    df["long_entry"] = (
        (df["fund8"] < I.FUND_LONG_THR) & hot & ~violent & conf_ok & valid
    )
    # reversing exits: the opposite-side entry closes the position
    df["long_exit"] = df["short_entry"]
    df["short_exit"] = df["long_entry"]
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
