"""Linear regression slope signals.

Long: the LinReg(20) slope turns positive (slope > 0 with the
previous bar's slope <= 0) AND R^2 >= 0.5. Short: mirror — slope
turns negative AND R^2 >= 0.5. Exit a long when the slope turns
negative (slope < 0) or R^2 falls below 0.3; exit a short when the
slope turns positive or R^2 falls below 0.3. All inputs are computed
from data through bar i's close, so signals on bar i use no future
data.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    slope = df["linreg_slope"]
    r2 = df["linreg_r2"]
    turn_pos = (slope > 0) & (slope.shift(1) <= 0)
    turn_neg = (slope < 0) & (slope.shift(1) >= 0)
    strong = (r2 >= 0.5).fillna(False)
    df["long_entry"] = (turn_pos & strong).fillna(False).astype(bool)
    df["short_entry"] = (turn_neg & strong).fillna(False).astype(bool)
    df["long_exit"] = ((slope < 0) | (r2 < 0.3)).fillna(False).astype(bool)
    df["short_exit"] = ((slope > 0) | (r2 < 0.3)).fillna(False).astype(bool)
    return df
