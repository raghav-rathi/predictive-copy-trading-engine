"""Value-area breakout indicators.

Each UTC day, a volume profile is built from the PRIOR completed
day's 24 hourly bars: 50 price bins across [day low, day high],
each bar's volume assigned to the bin containing its close. POC =
bin with max volume; expand outward from the POC adding bins until
cumulative volume >= 70% of the day's volume -> VAH (top edge of
the highest bin included), VAL (bottom edge of the lowest bin
included). The profile for day D is available from the 00:00 UTC
bar of day D (computed from day D-1, which has just completed) —
prior-day only, no lookahead. The profile is recomputed each UTC
day from the just-completed day.

Entry is acceptance, not a poke: long on the 2nd consecutive close
above VAH, short on the 2nd consecutive close below VAL. The
consecutive-close streak resets at each UTC day boundary (the
levels change) and whenever a close prints back inside the value
area.

Columns:
    vah / val -- value-area high/low of the active (prior-day)
        profile, NaN until the first full day completes
    poc -- point of control (centre of the max-volume bin)
    above_count / below_count -- consecutive closes above VAH /
        below VAL (0 when the last close was inside the area)
    long_trigger / short_trigger -- True only on the acceptance bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

N_BINS = 50
VALUE_PCT = 0.70
MS_PER_DAY = 86_400_000

INDICATOR_COLS = ["vah", "val", "poc", "above_count", "below_count", "atr"]


def _profile_from_day(closes, vols, lows, highs):
    """(vah, val, poc) from one completed day's bars."""
    day_low = min(lows)
    day_high = max(highs)
    total = float(sum(vols))
    if total <= 0 or day_high <= day_low:
        # Degenerate day (flat range or no volume): the value area
        # collapses to the day's range.
        return day_high, day_low, (day_high + day_low) / 2.0
    width = (day_high - day_low) / N_BINS
    bin_vol = np.zeros(N_BINS)
    for c, v in zip(closes, vols):
        idx = int((c - day_low) / (day_high - day_low) * N_BINS)
        idx = min(N_BINS - 1, max(0, idx))
        bin_vol[idx] += v
    poc_bin = int(np.argmax(bin_vol))
    target = VALUE_PCT * total
    lo = hi = poc_bin
    cum = bin_vol[poc_bin]
    while cum < target:
        up_vol = bin_vol[hi + 1] if hi + 1 < N_BINS else -1.0
        dn_vol = bin_vol[lo - 1] if lo - 1 >= 0 else -1.0
        if up_vol < 0 and dn_vol < 0:
            break
        # Add the heavier adjacent bin first (ties: expand down).
        if dn_vol >= up_vol:
            lo -= 1
            cum += bin_vol[lo]
        else:
            hi += 1
            cum += bin_vol[hi]
    vah = day_low + (hi + 1) * width
    val = day_low + lo * width
    poc = day_low + (poc_bin + 0.5) * width
    return vah, val, poc


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    t = df["t"].to_numpy(dtype=np.int64)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    vah = np.full(n, np.nan)
    val = np.full(n, np.nan)
    poc = np.full(n, np.nan)
    above_count = np.zeros(n, dtype=int)
    below_count = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    cur_day = None
    cur_vah = cur_val = cur_poc = np.nan
    day_closes, day_vols, day_lows, day_highs = [], [], [], []
    run_above = 0
    run_below = 0

    for i in range(n):
        day = int(t[i] // MS_PER_DAY)
        if day != cur_day:
            # A new UTC day starts: the day that just ended is
            # complete, so its profile becomes the active one.
            if cur_day is not None and day_closes:
                cur_vah, cur_val, cur_poc = _profile_from_day(
                    day_closes, day_vols, day_lows, day_highs
                )
            day_closes, day_vols, day_lows, day_highs = [], [], [], []
            cur_day = day
            run_above = 0
            run_below = 0
        day_closes.append(c[i])
        day_vols.append(v[i])
        day_lows.append(l[i])
        day_highs.append(h[i])

        vah[i] = cur_vah
        val[i] = cur_val
        poc[i] = cur_poc
        if not np.isnan(cur_vah):
            if c[i] > cur_vah:
                run_above += 1
                run_below = 0
            elif c[i] < cur_val:
                run_below += 1
                run_above = 0
            else:
                run_above = 0
                run_below = 0
            if run_above == 2:
                long_trig[i] = True
            if run_below == 2:
                short_trig[i] = True
        above_count[i] = run_above
        below_count[i] = run_below

    df["vah"] = vah
    df["val"] = val
    df["poc"] = poc
    df["above_count"] = above_count
    df["below_count"] = below_count
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
