"""Z-score mean reversion signals.

Long when z crosses back above -2 after being below -2 (stretched
oversold, reverting), with the SMA(50) slope flat-to-up. Short when z
crosses back below +2 after being above +2, with the SMA(50) slope
flat-to-down. Exit when z crosses 0 (back to the mean).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = (
        B.crossed_above(df["zscore"], -2.0) & df["sma50_slope_up"]
    ).astype(bool)
    df["short_entry"] = (
        B.crossed_below(df["zscore"], 2.0) & df["sma50_slope_down"]
    ).astype(bool)
    df["long_exit"] = B.crossed_above(df["zscore"], 0.0).astype(bool)
    df["short_exit"] = B.crossed_below(df["zscore"], 0.0).astype(bool)
    return df
