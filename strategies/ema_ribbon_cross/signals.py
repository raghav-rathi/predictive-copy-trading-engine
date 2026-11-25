"""EMA ribbon expansion signals.

Long when the ribbon is fully aligned bullish AND compression was
true within the last 3 bars (the ribbon just uncoiled upward);
short on the mirror. Exit when the fast end of the ribbon breaks
alignment (EMA8 crosses back through EMA13).

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (df["aligned_bull"] & df["comp_recent"]).fillna(False).astype(bool)
    df["short_entry"] = (df["aligned_bear"] & df["comp_recent"]).fillna(False).astype(bool)
    df["long_exit"] = (df["ema8"] < df["ema13"]).fillna(False).astype(bool)
    df["short_exit"] = (df["ema8"] > df["ema13"]).fillna(False).astype(bool)
    return df
