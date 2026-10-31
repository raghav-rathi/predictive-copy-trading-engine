"""Woodie daily pivot points, applied to 1h bars.

Each UTC calendar day's bars are grouped; for each completed day
H = max high, L = min low, C = last close. Levels for a day's bars
come from the PRIOR completed day only (shifted daily table), so the
first day has no levels and no signals:

    PP = (H + L + 2*C) / 4
    R1 = 2*PP - L
    S1 = 2*PP - H
    R2 = PP + (H - L)
    S2 = PP - (H - L)

The prior day's levels are forward-filled (constant) across the
current day's bars. Because a day's levels are fixed before that
day's first bar, the construction is strictly causal.

Columns:
    pp, r1, s1, r2, s2 -- prior-day Woodie levels (NaN on day 1)
    atr               -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    day = pd.to_datetime(df["t"], unit="ms", utc=True).dt.floor("D")
    daily = pd.DataFrame({
        "day": day.to_numpy(),
        "H": df["h"].to_numpy(),
        "L": df["l"].to_numpy(),
        "C": df["c"].to_numpy(),
    }).groupby("day", as_index=False).agg(
        H=("H", "max"), L=("L", "min"), C=("C", "last"))
    daily = daily.sort_values("day").reset_index(drop=True)
    prior = daily[["H", "L", "C"]].shift(1)
    pp = (prior["H"] + prior["L"] + 2 * prior["C"]) / 4
    levels = pd.DataFrame({
        "day": daily["day"],
        "pp": pp,
        "r1": 2 * pp - prior["L"],
        "s1": 2 * pp - prior["H"],
        "r2": pp + (prior["H"] - prior["L"]),
        "s2": pp - (prior["H"] - prior["L"]),
    })
    # Left merge preserves the bars' order, so positional assignment
    # is safe regardless of the frame's index.
    merged = pd.DataFrame({"day": day.to_numpy()}).merge(
        levels, on="day", how="left")
    for col in ("pp", "r1", "s1", "r2", "s2"):
        df[col] = merged[col].to_numpy(dtype=float)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
