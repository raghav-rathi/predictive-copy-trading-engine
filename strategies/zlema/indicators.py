"""Zero Lag EMA ZLEMA(20) vs ZLEMA(50) indicators."""

import pandas as pd

from strategies import base as B

INDICATOR_COLS = ["zlema20", "zlema50"]


def zlema_series(c: pd.Series, n: int) -> pd.Series:
    """Zero Lag EMA: EMA of the de-lagged series 2*close - close shifted by lag.

    lag = (n - 1) / 2 rounded.
    """
    lag = int(round((n - 1) / 2))
    delagged = 2 * c - c.shift(lag)
    return B.ema(delagged, n)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["zlema20"] = zlema_series(df["c"], 20)
    df["zlema50"] = zlema_series(df["c"], 50)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
