"""SineWave signals: long on sine crossing above lead sine, short on
crossing below; exits on the opposite cross (Ehlers' cycle-mode rule).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = crossed_above(df["sine"], df["lead_sine"])
    dn = crossed_below(df["sine"], df["lead_sine"])
    df["long_entry"] = up.fillna(False).astype(bool)
    df["short_entry"] = dn.fillna(False).astype(bool)
    df["long_exit"] = dn.fillna(False).astype(bool)
    df["short_exit"] = up.fillna(False).astype(bool)
    return df
