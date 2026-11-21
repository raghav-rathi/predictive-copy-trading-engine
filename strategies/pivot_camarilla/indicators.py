"""Camarilla Pivot Breakout indicators.

Nick Scott, Camarilla Equation (1989). Levels for the current UTC
day come from the PRIOR completed UTC day only:

    R3 = C_prev + (H_prev - L_prev) * 1.055
    S3 = C_prev - (H_prev - L_prev) * 1.055

where H_prev / L_prev / C_prev are the prior completed day's high /
low / close. Bars are grouped by UTC date from t. No levels exist
before the first full day completes: bars in the first UTC day have
NaN levels and no signals.

NOTE on the 1.055 factor: the canonical Camarilla R3 uses
(H - L) * 1.1 / 4 = (H - L) * 0.275 (Babypips / TradingView). The
spec assigned here uses 1.055, which is ~3.8x the canonical R3
offset and close to the canonical R4 offset (1.1 / 2 = 0.55) doubled;
it is implemented exactly as assigned and the difference is
documented in CALIBRATION.md (the 0.275 canonical factor is run
there as robustness alternate Alt-A).

Columns:
    r3 / s3 -- Camarilla R3 / S3 levels for the current UTC day
    prev_day_h / prev_day_l / prev_day_c -- prior completed day's H/L/C
    atr -- Wilder ATR(14) for the risk layer

No lookahead: a bar's levels come only from days that completed
before the bar's own day started; the level for a day is fixed for
the whole day and only changes at a UTC-day boundary.
"""

import numpy as np
import pandas as pd

from strategies import base as B

R3_FACTOR = 1.055
ATR_N = 14


def add_indicators(df: pd.DataFrame, r3_factor: float = R3_FACTOR,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]

    # UTC day key for each bar.
    dt = pd.to_datetime(df["t"], unit="ms", utc=True)
    day = dt.dt.normalize()
    day_key = pd.Series(day.to_numpy(), index=df.index)

    # Per-day aggregates: high, low, and last close of the day.
    daily = pd.DataFrame({
        "H": h.groupby(day_key).max(),
        "L": l.groupby(day_key).min(),
        "C": c.groupby(day_key).last(),
    })
    prev = daily.shift(1)  # prior COMPLETED day only
    prev_h = day_key.map(prev["H"].to_dict())
    prev_l = day_key.map(prev["L"].to_dict())
    prev_c = day_key.map(prev["C"].to_dict())
    df["prev_day_h"] = prev_h
    df["prev_day_l"] = prev_l
    df["prev_day_c"] = prev_c
    rng = prev_h - prev_l
    df["r3"] = prev_c + rng * r3_factor
    df["s3"] = prev_c - rng * r3_factor
    df["atr"] = B.atr(h, l, c, atr_n)
    return df
