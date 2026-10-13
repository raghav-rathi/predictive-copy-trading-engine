"""Linda Raschke & Larry Connors 'Holy Grail' indicators (Street Smarts, Ch.10).

Trend filter: ADX(14) > 30 and rising. The setup waits for the first pullback
that touches the 20-period EMA; a buy stop then sits above the touch bar's
high, with the protective stop at the newly formed swing low. This module
computes the regime columns; the touch/breakout state machine lives in
signals.py. Pure pandas/numpy, no lookahead.
"""

import pandas as pd

from strategies import base as B

ADX_LEN = 14
ADX_MIN = 30.0
EMA_LEN = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = B.adx(df["h"], df["l"], df["c"], ADX_LEN)
    df["adx"] = d["adx"]
    df["plus_di"] = d["plus_di"]
    df["minus_di"] = d["minus_di"]
    df["adx_prev"] = df["adx"].shift(1)
    df["ema20"] = B.ema(df["c"], EMA_LEN)
    return df
