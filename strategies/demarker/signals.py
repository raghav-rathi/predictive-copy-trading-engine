"""DeMarker exhaustion signals.

Entry (exhaustion reversal):
    long_entry  = DeM crosses BELOW 0.3 (prev DeM >= 0.3, now < 0.3)
                  -- downside momentum exhausted at oversold.
    short_entry = DeM crosses ABOVE 0.7 (prev DeM <= 0.7, now > 0.7)
                  -- upside momentum exhausted at overbought.

Exit (mean reversion complete / wrong):
    long_exit  = DeM crosses ABOVE 0.5 (reversion to neutral complete)
                 OR DeM > 0.7 (price ran away overbought -- take the money).
    short_exit = DeM crosses BELOW 0.5 OR DeM < 0.3.
Risk-level exits (2xATR stop, 24-bar max hold) come from risk.py.
"""

import pandas as pd

OS_LEVEL = 0.3   # oversold exhaustion
OB_LEVEL = 0.7   # overbought exhaustion
MID_LEVEL = 0.5  # mean-reversion target


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dem = df["dem"]
    prev = dem.shift(1)
    df["long_entry"] = ((prev >= OS_LEVEL) & (dem < OS_LEVEL)).fillna(False)
    df["short_entry"] = ((prev <= OB_LEVEL) & (dem > OB_LEVEL)).fillna(False)
    cross_up_mid = ((prev <= MID_LEVEL) & (dem > MID_LEVEL)).fillna(False)
    cross_dn_mid = ((prev >= MID_LEVEL) & (dem < MID_LEVEL)).fillna(False)
    df["long_exit"] = (cross_up_mid | (dem > OB_LEVEL)).fillna(False)
    df["short_exit"] = (cross_dn_mid | (dem < OS_LEVEL)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
