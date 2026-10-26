"""Soldiers long, crows short, opposite pattern exits."""

import numpy as np
import pandas as pd


def _three(df, sign):
    o, c = df["o"], df["c"]
    body = df["body"]
    if sign > 0:
        strong = body > 0.003 * c
        rising = (c > c.shift(1)) & (c.shift(1) > c.shift(2))
        inside = (o > o.shift(1)) & (o < c.shift(1)) & (o.shift(1) > o.shift(2)) & (o.shift(1) < c.shift(2))
    else:
        strong = body < -0.003 * c
        rising = (c < c.shift(1)) & (c.shift(1) < c.shift(2))
        inside = (o < o.shift(1)) & (o > c.shift(1)) & (o.shift(1) < o.shift(2)) & (o.shift(1) > c.shift(2))
    return (strong & strong.shift(1) & strong.shift(2) & rising & inside).fillna(False)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_e = _three(df, +1)
    short_e = _three(df, -1)
    df["long_entry"] = long_e.to_numpy(dtype=bool)
    df["short_entry"] = short_e.to_numpy(dtype=bool)
    df["long_exit"] = short_e.to_numpy(dtype=bool)
    df["short_exit"] = long_e.to_numpy(dtype=bool)
    return df
