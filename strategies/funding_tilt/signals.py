"""Funding tilt signals (contrarian).

Long  when funding z-score < -2 (extremely negative = crowded shorts)
Short when funding z-score > +2 (extremely positive = crowded longs)
Exit when |z| < 0.5 (crowding resolved).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["fund_z"].notna()
    df["long_entry"] = (df["fund_z"] < -2.0) & valid
    df["short_entry"] = (df["fund_z"] > 2.0) & valid
    df["long_exit"] = df["fund_z"].abs() < 0.5
    df["short_exit"] = df["fund_z"].abs() < 0.5
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
