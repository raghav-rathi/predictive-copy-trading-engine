"""ICT Power of Three / AMD indicators (Michael J. Huddleston).

Per UTC calendar day from 1h bars (crypto trades 24/7, so there are
no New York sessions to anchor to — the UTC day is the session; see
CALIBRATION.md):

    ACCUMULATION  = the range of the first 8 hours (00:00-08:00 UTC)
    MANIPULATION  = a sweep of the range low/high by >= 0.25 x ATR(14)
                    during 08:00-16:00 UTC
    DISTRIBUTION  = price closing back through the range in the
                    opposite direction of the sweep during
                    16:00-24:00 UTC (see signals.py)

Causality: the accumulation range is the expanding high/low of the
day's first-8-hours bars while the day is still in that window, and
freezes to the completed first-8-hours range for bars from 08:00
onward — a bar never sees its own day's later values. Sweep flags
are carried forward within the day from the sweep bar and reset at
the next UTC midnight. When a day sweeps both sides, the FIRST sweep
in time wins; a same-bar tie on both sides yields no direction.

Columns:

    pot_hour        -- UTC hour of the bar (0-23)
    pot_day_start   -- UTC midnight starting the bar's day (ms)
    pot_acc_high, pot_acc_low -- accumulation range (see above)
    pot_swept_low, pot_swept_high -- a low/high sweep has occurred
                    this UTC day (first sweep wins)
    atr (Wilder ATR(14) for the risk layer and the sweep threshold)

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ACCUM_HOURS = 8
MANIP_START = 8
MANIP_END = 16
SWEEP_ATR_MULT = 0.25

INDICATOR_COLS = ["pot_hour", "pot_day_start", "pot_acc_high",
                  "pot_acc_low", "pot_swept_low", "pot_swept_high",
                  "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    dt = pd.to_datetime(df["t"], unit="ms", utc=True)
    day = dt.dt.floor("D")
    hour = dt.dt.hour.to_numpy()
    day_start = day.astype("int64").to_numpy() // 1_000_000

    atr = B.atr(df["h"], df["l"], df["c"], 14)

    # Accumulation range: expanding within the first 8 hours, frozen
    # to the completed first-8-hours range from 08:00 onward.
    first8 = hour < ACCUM_HOURS
    day_key = day.to_numpy()
    partial_high = df["h"].groupby(day_key).cummax()
    partial_low = df["l"].groupby(day_key).cummin()
    frozen_high = df.loc[first8, "h"].groupby(day_key[first8]).max()
    frozen_low = df.loc[first8, "l"].groupby(day_key[first8]).min()
    acc_high = np.where(
        hour >= ACCUM_HOURS,
        pd.Series(day_key).map(frozen_high).to_numpy(),
        partial_high.to_numpy())
    acc_low = np.where(
        hour >= ACCUM_HOURS,
        pd.Series(day_key).map(frozen_low).to_numpy(),
        partial_low.to_numpy())

    # Manipulation: sweep of the range extreme by >= 0.25 x ATR(14)
    # during 08:00-16:00 UTC. First sweep of the day wins.
    in_manip = (hour >= MANIP_START) & (hour < MANIP_END)
    sweep_low_event = in_manip & ((acc_low - df["l"].to_numpy()) >= SWEEP_ATR_MULT * atr.to_numpy())
    sweep_high_event = in_manip & ((df["h"].to_numpy() - acc_high) >= SWEEP_ATR_MULT * atr.to_numpy())
    idx = np.arange(n)
    low_first = pd.Series(np.where(sweep_low_event, idx, np.inf)).groupby(day_key).transform("min").to_numpy()
    high_first = pd.Series(np.where(sweep_high_event, idx, np.inf)).groupby(day_key).transform("min").to_numpy()
    swept_low = (low_first < high_first) & (idx >= low_first)
    swept_high = (high_first < low_first) & (idx >= high_first)

    df["pot_hour"] = hour
    df["pot_day_start"] = day_start
    df["pot_acc_high"] = acc_high
    df["pot_acc_low"] = acc_low
    df["pot_swept_low"] = swept_low
    df["pot_swept_high"] = swept_high
    df["atr"] = atr
    return df
