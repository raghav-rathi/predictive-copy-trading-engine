"""Bullish harami long, bearish harami short, opposite exits."""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, c = df["o"], df["c"]
    po, pc = o.shift(1), c.shift(1)
    big = (pc - po).abs() > 0.01 * pc
    inside = (o > po.where(pc > po, pc)) & (o < pc.where(pc > po, po)) & (c > po.where(pc > po, pc)) & (c < pc.where(pc > po, po))
    small = (c - o).abs() < 0.5 * (pc - po).abs()
    bullish = (pc < po) & (c > o) & big & inside & small
    bearish = (pc > po) & (c < o) & big & inside & small
    df["long_entry"] = bullish.fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = bearish.fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = bearish.fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = bullish.fillna(False).to_numpy(dtype=bool)
    return df
