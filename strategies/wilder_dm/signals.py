"""Wilder DMI signals.

Long:  +DI crosses above -DI with ADX > 25 and rising.
Short: mirror.
Exits: Parabolic SAR flip against the position, ADX < 20, or Wilder's range
rule (ADX below both DI lines = trendless).
"""

import pandas as pd

from strategies import base as B

ADX_MIN = 25.0
ADX_DEAD = 20.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rising = df["adx"] > df["adx_prev"]
    gate = (df["adx"] > ADX_MIN) & rising
    df["long_entry"] = B.crossed_above(df["plus_di"], df["minus_di"]) & gate
    df["short_entry"] = B.crossed_below(df["plus_di"], df["minus_di"]) & gate
    sar_flip_dn = (df["sar_trend"] == -1) & (df["sar_trend_prev"] == 1)
    sar_flip_up = (df["sar_trend"] == 1) & (df["sar_trend_prev"] == -1)
    range_rule = (df["adx"] < df["plus_di"]) & (df["adx"] < df["minus_di"])
    adx_dead = df["adx"] < ADX_DEAD
    df["long_exit"] = sar_flip_dn | adx_dead | range_rule
    df["short_exit"] = sar_flip_up | adx_dead | range_rule
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
