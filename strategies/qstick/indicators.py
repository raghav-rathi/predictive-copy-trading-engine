"""Tushar Chande's Qstick indicators.

Qstick quantifies candlestick trend numerically: the n-period moving
average of each bar's body (close - open). Positive means most of the
last n bars closed up (buying pressure); negative means the reverse.
An n-period moving average of Qstick itself acts as the trigger/signal
line. All causal: only data through bar i's close.
"""

import pandas as pd

from strategies import base as B

N = 8  # Chande's default Qstick period
TRIGGER = 8  # signal-line period on Qstick itself


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    body = df["c"] - df["o"]
    df["qstick"] = B.sma(body, N)
    df["qstick_trigger"] = B.sma(df["qstick"], TRIGGER)
    return df
