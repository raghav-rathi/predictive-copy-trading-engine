"""Heikin-Ashi signals (Valcu).

Long: previous HA bar red, current HA bar green, current bar NOT a
consolidation bar. Short: mirror. No entries during consolidation bars.
Exit/flatten: opposite-color HA bar OR a consolidation bar.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_red = df["ha_red"].shift(1).fillna(False)
    prev_green = df["ha_green"].shift(1).fillna(False)
    consol = df["ha_consol"].fillna(False)
    df["long_entry"] = (prev_red & df["ha_green"] & (~consol)).fillna(False)
    df["short_entry"] = (prev_green & df["ha_red"] & (~consol)).fillna(False)
    df["long_exit"] = (df["ha_red"] | consol).fillna(False)
    df["short_exit"] = (df["ha_green"] | consol).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
