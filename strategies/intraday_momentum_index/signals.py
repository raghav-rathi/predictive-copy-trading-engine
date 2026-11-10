"""Intraday Momentum Index threshold signals (RSI-style).

Long:  IMI crosses up through 30 (leaving oversold).
Short: IMI crosses down through 70 (leaving overbought).
Exit a long on IMI crossing above 70; exit a short on IMI crossing
below 30. All inputs are computed from data through bar i's close,
so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.intraday_momentum_index.indicators import IMI_PERIOD  # noqa: F401  (re-exported for tests)

OVERSOLD = 30.0
OVERBOUGHT = 70.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up_30 = crossed_above(df["imi"], OVERSOLD)
    cross_down_70 = crossed_below(df["imi"], OVERBOUGHT)
    cross_up_70 = crossed_above(df["imi"], OVERBOUGHT)
    cross_down_30 = crossed_below(df["imi"], OVERSOLD)
    df["long_entry"] = cross_up_30.fillna(False).astype(bool)
    df["short_entry"] = cross_down_70.fillna(False).astype(bool)
    df["long_exit"] = cross_up_70.fillna(False).astype(bool)
    df["short_exit"] = cross_down_30.fillna(False).astype(bool)
    return df
