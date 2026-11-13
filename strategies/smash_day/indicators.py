"""Smash Day indicators (Larry Williams, Long-Term Secrets to Short-Term Trading, 1999).

A Smash Day setup is built from completed UTC-day bars:

    inside day  -- a day whose high is below the prior day's high AND whose
                   low is above the prior day's low (a contraction day).
    wide day    -- the day before the inside day had a range larger than
                   1.5x the trailing 20-day mean daily range (an expansion
                   day: the market made a big move, then went quiet).
    setup       -- trade the break of the inside day's high/low during the
                   two days after the inside day (Williams trades the next
                   day; the second day is allowed because a 1h-bar break
                   can arrive late on 24/7 crypto, and the window is fixed
                   a priori, not tuned).

All columns are causal: for a 1h bar in UTC day d, only completed days
d-1, d-2, ... are used. The current day's own high/low never enter any
column. Days are UTC calendar days (crypto trades 24/7, so there is no
session open to anchor to; the UTC day is the documented adaptation).

Columns:

    prev_day_high, prev_day_low -- high/low of the last completed day
    day_before_high, day_before_low -- high/low of the day before that
    prev_day_range, day_before_range -- their ranges
    mean_range_20 -- trailing 20-day mean daily range (through day d-2)
    inside_day -- prev day inside the day before it
    wide_day -- the day before the inside day was wide (> 1.5x mean range)
    setup_active -- a smash setup is live for this bar's day
    inside_high, inside_low -- the inside day's range to break
    atr -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

DAY_MS = 86_400_000
WIDE_MULT = 1.5
MEAN_RANGE_N = 20
SETUP_VALID_DAYS = 2

INDICATOR_COLS = [
    "prev_day_high", "prev_day_low",
    "day_before_high", "day_before_low",
    "prev_day_range", "day_before_range",
    "mean_range_20", "inside_day", "wide_day",
    "setup_active", "inside_high", "inside_low", "atr",
]


def _daily_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per completed UTC day: high, low, range. Indexed by day number."""
    day = (df["t"] // DAY_MS).to_numpy()
    tmp = pd.DataFrame({"day": day, "h": df["h"].to_numpy(), "l": df["l"].to_numpy()})
    g = tmp.groupby("day").agg(dh=("h", "max"), dl=("l", "min"))
    g["dr"] = g["dh"] - g["dl"]
    return g


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    day = (df["t"] // DAY_MS).to_numpy()
    daily = _daily_table(df)

    # Per-bar lookup of completed-day values: prev = day d-1, before = day d-2.
    idx = pd.Index(day)
    prev = daily.reindex(idx - 1)
    before = daily.reindex(idx - 2)
    prev_vals = prev.reset_index(drop=True)
    before_vals = before.reset_index(drop=True)

    df["prev_day_high"] = prev_vals["dh"].to_numpy()
    df["prev_day_low"] = prev_vals["dl"].to_numpy()
    df["day_before_high"] = before_vals["dh"].to_numpy()
    df["day_before_low"] = before_vals["dl"].to_numpy()
    df["prev_day_range"] = df["prev_day_high"] - df["prev_day_low"]
    df["day_before_range"] = df["day_before_high"] - df["day_before_low"]

    # Trailing 20-day mean range through the day-before (shifted so the
    # inside day's own range never enters its own wide test).
    mean_range = daily["dr"].rolling(MEAN_RANGE_N, min_periods=MEAN_RANGE_N).mean()
    df["mean_range_20"] = mean_range.reindex(idx - 2).reset_index(drop=True).to_numpy()

    inside = (df["prev_day_high"] < df["day_before_high"]) & (
        df["prev_day_low"] > df["day_before_low"]
    )
    wide = df["day_before_range"] > WIDE_MULT * df["mean_range_20"]
    df["inside_day"] = inside.fillna(False)
    df["wide_day"] = wide.fillna(False)

    # Setup is live for a day if that day's prev-day pair forms an
    # inside+wide setup, or the previous day did (2-day validity window).
    # Compute per-day setup flag, then map to bars.
    per_day = pd.DataFrame(
        {"inside": df["inside_day"].to_numpy(), "wide": df["wide_day"].to_numpy()},
        index=idx,
    )
    # One row per day (all bars in a day share the flag).
    day_setup = per_day.groupby(level=0).first()
    day_setup["setup"] = day_setup["inside"] & day_setup["wide"]
    setup_today = day_setup["setup"].reindex(idx).to_numpy()
    setup_yday = day_setup["setup"].reindex(idx - 1).to_numpy()
    df["setup_active"] = (np.nan_to_num(setup_today, nan=False).astype(bool)
                          | np.nan_to_num(setup_yday, nan=False).astype(bool))

    df["inside_high"] = df["prev_day_high"]
    df["inside_low"] = df["prev_day_low"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
