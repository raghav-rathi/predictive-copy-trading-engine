"""Judas swing (ICT session-open fakeout reversal) indicators.

Per UTC day, the Asian range is the high/low of the prior evening's
bars with UTC hour in [20, 24) (the 20:00, 21:00, 22:00 and 23:00
bars). The London window is the bars with UTC hour in [7, 10).

Bullish Judas: within the London window a bar's low sweeps below
the Asian low (a wick below the range), a later close gets back
above the Asian low (reclaim), then a close above the highest high
printed since the sweep bar (bars after the sweep bar, before the
current bar) is the structure shift -> long_trigger. Bearish is the
mirror (sweep above the Asian high, reclaim close back below it,
close below the lowest low printed since the sweep bar).

Entries are valid only until 12:00 UTC (trigger checks require
hour < 12); one signal per UTC day per side. The sweep / reclaim /
shift may straddle the 10:00 window end, but the sweep itself must
occur inside the window. A deeper sweep before any reclaim moves
the sweep extreme and restarts the "since sweep" extreme.

Columns:
    asian_high, asian_low -- prior evening's range (NaN until the
        first complete evening is in the frame)
    judas_state -- 0 none, 1 swept, 2 reclaimed (max over sides)
    judas_side  -- +1 bearish setup furthest along, -1 bullish, 0 none
    long_trigger / short_trigger -- True only on the entry bar
    last_bull_sweep_low / last_bear_sweep_high -- most recent sweep
        extreme, forward-filled (invalidation level for the exit rule)
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

WINDOW_START = 7   # London window opens 07:00 UTC
WINDOW_END = 10    # London window closes 10:00 UTC (bars 07, 08, 09)
ENTRY_DEADLINE = 12  # entries valid only while hour < 12

INDICATOR_COLS = ["asian_high", "asian_low", "judas_state",
                  "long_trigger", "short_trigger", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    times = pd.to_datetime(df["t"], unit="ms", utc=True)
    hours = times.dt.hour.to_numpy(dtype=int)
    days = times.dt.floor("D")

    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    # Per-day Asian range from the prior evening's bars (hour 20-23).
    evening = {}
    tmp = pd.DataFrame({"day": days.to_numpy(), "hour": hours, "h": h, "l": l})
    for day, grp in tmp[tmp["hour"] >= 20].groupby("day"):
        evening[day] = (float(grp["h"].max()), float(grp["l"].min()))

    asian_high = np.full(n, np.nan)
    asian_low = np.full(n, np.nan)
    judas_state = np.zeros(n, dtype=int)
    judas_side = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)
    last_bull_sweep = np.full(n, np.nan)
    last_bear_sweep = np.full(n, np.nan)

    cur_day = None
    # Bullish per-day state.
    b_swept = b_reclaimed = b_fired = False
    b_sweep_low = np.nan
    b_sweep_bar = -1
    b_since_high = -np.inf
    # Bearish per-day state (mirror).
    s_swept = s_reclaimed = s_fired = False
    s_sweep_high = np.nan
    s_sweep_bar = -1
    s_since_low = np.inf
    cur_bull_sweep = np.nan
    cur_bear_sweep = np.nan

    for i in range(n):
        day = days.iloc[i]
        if day != cur_day:
            cur_day = day
            b_swept = b_reclaimed = b_fired = False
            b_sweep_low = np.nan
            b_sweep_bar = -1
            b_since_high = -np.inf
            s_swept = s_reclaimed = s_fired = False
            s_sweep_high = np.nan
            s_sweep_bar = -1
            s_since_low = np.inf
        rng = evening.get(day - pd.Timedelta(days=1))
        if rng is not None:
            asian_high[i], asian_low[i] = rng
            ah, al = rng

            # ---- bullish machine ----
            if not b_fired:
                if not b_swept:
                    if WINDOW_START <= hours[i] < WINDOW_END and l[i] < al:
                        b_swept = True
                        b_sweep_low = l[i]
                        b_sweep_bar = i
                        cur_bull_sweep = l[i]
                else:
                    if not b_reclaimed and l[i] < b_sweep_low:
                        # Deeper sweep before any reclaim: move the
                        # extreme and restart the "since" extreme.
                        b_sweep_low = l[i]
                        b_sweep_bar = i
                        b_since_high = -np.inf
                        cur_bull_sweep = l[i]
                    if not b_reclaimed:
                        if c[i] > al:
                            b_reclaimed = True
                    elif hours[i] < ENTRY_DEADLINE and np.isfinite(b_since_high):
                        if c[i] > b_since_high:
                            long_trig[i] = True
                            b_fired = True
            # ---- bearish machine (mirror) ----
            if not s_fired:
                if not s_swept:
                    if WINDOW_START <= hours[i] < WINDOW_END and h[i] > ah:
                        s_swept = True
                        s_sweep_high = h[i]
                        s_sweep_bar = i
                        cur_bear_sweep = h[i]
                else:
                    if not s_reclaimed and h[i] > s_sweep_high:
                        s_sweep_high = h[i]
                        s_sweep_bar = i
                        s_since_low = np.inf
                        cur_bear_sweep = h[i]
                    if not s_reclaimed:
                        if c[i] < ah:
                            s_reclaimed = True
                    elif hours[i] < ENTRY_DEADLINE and np.isfinite(s_since_low):
                        if c[i] < s_since_low:
                            short_trig[i] = True
                            s_fired = True

            # Fold this bar into the "since sweep" extremes, but only
            # for bars after the sweep bar.
            if b_swept and not b_fired and i > b_sweep_bar:
                b_since_high = max(b_since_high, h[i])
            if s_swept and not s_fired and i > s_sweep_bar:
                s_since_low = min(s_since_low, l[i])

        b_code = 2 if b_reclaimed else (1 if b_swept else 0)
        s_code = 2 if s_reclaimed else (1 if s_swept else 0)
        judas_state[i] = max(b_code, s_code)
        if b_code > s_code:
            judas_side[i] = -1
        elif s_code > b_code:
            judas_side[i] = 1
        else:
            judas_side[i] = 0
        last_bull_sweep[i] = cur_bull_sweep
        last_bear_sweep[i] = cur_bear_sweep

    df["asian_high"] = asian_high
    df["asian_low"] = asian_low
    df["judas_state"] = judas_state
    df["judas_side"] = judas_side
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    df["last_bull_sweep_low"] = last_bull_sweep
    df["last_bear_sweep_high"] = last_bear_sweep
    return df
