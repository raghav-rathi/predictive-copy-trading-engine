"""Fisher ACD opening-range indicators.

Mark Fisher, "The Logical Trader" (ACD method): the opening range (OR)
of a session sets the day's tone. A points (entry) sit a fraction of an
ATR outside the OR; C points sit further out; B/D points (the OR edges
themselves) are exits. Adapted here to 24/7 crypto on 1h bars, with the
UTC day (00:00-01:00 UTC bar = OR bar) as the session.

Pipeline (all causal, bar i uses only data through bar i's close):
  day       = UTC calendar day of bar i (from t, ms)
  or_high   = high of the first 1h bar of bar i's UTC day
  or_low    = low  of the first 1h bar of bar i's UTC day
  atr14     = Wilder ATR(14) from strategies.base
  a_up      = or_high + 0.5 * atr14
  a_down    = or_low  - 0.5 * atr14
  c_up      = or_high + 1.5 * atr14
  c_down    = or_low  - 1.5 * atr14
  pivot     = (previous UTC day's high + low + close) / 3
  day_index = 0-based position of bar i within its UTC day

The OR levels are the first bar's high/low, so they are known once the
day's first bar closes and stay fixed for the whole day; the pivot uses
only the previous (completed) UTC day. Nothing here looks ahead: the
OR is taken from the day's first bar (<= bar i) and the pivot from the
previous day.
"""

import numpy as np
import pandas as pd

from strategies.base import atr

ATR_WINDOW = 14
A_ATR_MULT = 0.5
C_ATR_MULT = 1.5
MS_PER_DAY = 86_400_000

INDICATOR_COLS = [
    "atr14",
    "or_high",
    "or_low",
    "a_up",
    "a_down",
    "c_up",
    "c_down",
    "pivot_prev_day",
    "day_index",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = df["t"].to_numpy(dtype=np.int64)
    day_key = t // MS_PER_DAY
    day = pd.Series(day_key, index=df.index)

    # Opening range: high/low of the first bar of each UTC day.
    # groupby.transform("first") only ever reads the day's first bar,
    # which is at or before bar i, so this is causal.
    df["or_high"] = df.groupby(day)["h"].transform("first")
    df["or_low"] = df.groupby(day)["l"].transform("first")
    df["day_index"] = df.groupby(day).cumcount().astype(int)

    # Wilder ATR(14).
    df["atr14"] = atr(df["h"], df["l"], df["c"], ATR_WINDOW)

    a = df["atr14"]
    df["a_up"] = df["or_high"] + A_ATR_MULT * a
    df["a_down"] = df["or_low"] - A_ATR_MULT * a
    df["c_up"] = df["or_high"] + C_ATR_MULT * a
    df["c_down"] = df["or_low"] - C_ATR_MULT * a

    # Daily pivot from the previous (completed) UTC day.
    daily = df.groupby(day).agg(
        day_high=("h", "max"), day_low=("l", "min"), day_close=("c", "last")
    )
    daily_pivot = (daily["day_high"] + daily["day_low"] + daily["day_close"]) / 3
    # Map each day to the previous day's pivot in sorted day order, so a
    # missing calendar day cannot silently shift the pivot by one.
    days_sorted = sorted(daily_pivot.index.tolist())
    prev_pivot = {d: np.nan for d in days_sorted}
    for prev_d, d in zip(days_sorted, days_sorted[1:]):
        prev_pivot[d] = daily_pivot.loc[prev_d]
    df["pivot_prev_day"] = day.map(prev_pivot).astype(float)

    return df
