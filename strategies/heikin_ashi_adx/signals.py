"""Heikin Ashi trend + Wilder ADX filter signals.

Long: the Heikin Ashi bar is bullish (ha_close > ha_open)
AND ADX(14) > 25 (a real trend, not chop) AND +DI > -DI
(the trend points up). Short: the HA bar is bearish AND
ADX(14) > 25 AND -DI > +DI. Exit: the HA bar flips against
the position (long exits on a bearish HA bar, short on a
bullish one) OR ADX falls below 20 (the trend has died).

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness). The entry is a
level condition, not a cross: while the trend persists the
signal stays true, and the harness (one position at a time,
flat between trades) takes the first bar after going flat.
"""

import pandas as pd

ADX_ENTRY = 25.0
ADX_EXIT = 20.0


def add_signals(
    df: pd.DataFrame,
    adx_entry: float = ADX_ENTRY,
    adx_exit: float = ADX_EXIT,
) -> pd.DataFrame:
    df = df.copy()
    green = df["ha_close"] > df["ha_open"]
    red = df["ha_close"] < df["ha_open"]
    strong = df["adx"] > adx_entry
    df["long_entry"] = (
        green & strong & (df["plus_di"] > df["minus_di"])
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        red & strong & (df["minus_di"] > df["plus_di"])
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        red | (df["adx"] < adx_exit)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        green | (df["adx"] < adx_exit)
    ).fillna(False).astype(bool)
    return df
