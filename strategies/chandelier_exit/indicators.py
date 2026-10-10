"""Chandelier Exit indicators (Chuck LeBeau).

Classic LeBeau chandelier: a volatility stop hung from the rolling 22-bar
highest high (for longs) / lowest low (for shorts), 3 x ATR(22) away:

    chand_long  = HH22 - 3.0 * ATR22
    chand_short = LL22 + 3.0 * ATR22

No lookahead: HH22/LL22 are computed over the prior 22 bars EXCLUDING the
current bar (shift(1)), so bar i's line uses only data through bar i-1's
close. ATR22 is Wilder ATR, also through bar i's close.
"""

import pandas as pd

from strategies import base as B

LOOKBACK = 22
ATR_N = 22
MULT = 3.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    ll = df["l"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    atr = B.atr(df["h"], df["l"], df["c"], ATR_N)
    df["hh22"] = hh
    df["ll22"] = ll
    df["atr22"] = atr
    df["chand_long"] = hh - MULT * atr
    df["chand_short"] = ll + MULT * atr
    return df
