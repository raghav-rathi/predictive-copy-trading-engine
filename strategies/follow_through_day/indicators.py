"""Follow-Through Day indicators (William O'Neil, CANSLIM market direction).

One "day" = 24 hourly bars, UTC-midnight aligned. Each UTC day is
aggregated into:

    d_close -- close of the day's 23:00 bar
    d_low   -- minimum low of the day
    d_vol   -- sum of the day's 24 volumes

Daily state machine (values below are daily; they are surfaced on
1h bars only on the 23:00 bar that completes the day, so nothing
leaks intraday):

    corr_gate -- d_close <= (1 - 0.08) * trailing 20-day max of
                 d_close (max including the current day; needs
                 20 days of history). The market is >= 8% below
                 its 20-day high: a correction is on.
    new_low   -- d_low <= trailing 20-day min of d_low EXCLUDING
                 the current day (min of the prior 20 days).
                 The day made a new 20-day low.
    awaiting  -- set on a new-low day while corr_gate is/was true;
                 the low of that day becomes the candidate
                 attempt_low. Updated if a later day makes a new
                 20-day low before any up day.
    day 1     -- the first day AFTER a new-low day that closes UP
                 (d_close > prior day d_close) while awaiting.
                 attempt_low = d_low of the day immediately
                 BEFORE day 1 (the new-low day). Documented
                 choice: the single prior day's low, NOT the min
                 over all correction days -- the prior day is the
                 day that printed the 20-day low, so undercutting
                 it is a fresh 20-day low by construction.
    attempt   -- attempt_day counts 1, 2, 3, ... from day 1.
                 FAILS and resets if any later day's d_low
                 undercuts attempt_low (checked on attempt-days
                 2-7; day 1's own intraday dip below the prior
                 day's low does not fail it -- the check applies
                 to later days, per the brief). Expires after
                 attempt_day 7 with no FTD. On failure the
                 undercutting day becomes a fresh awaiting low
                 (it is itself a new 20-day low).
    FTD       -- on attempt-day 4-7, a day with day return
                 (d_close / prior d_close - 1) >= gain_pct
                 (1.5% shipped) AND d_vol > prior day d_vol.
                 ftd_day is True ONLY on that day's 23:00 bar;
                 the attempt then ends (confirmed, no re-fire).

Per-bar columns (all causal, no lookahead):

    d_close -- at a 23:00 bar: that day's close; on any other bar:
               the prior completed day's close (NaN before the
               first completed day).
    d_low   -- running minimum low of the current UTC day through
               the current bar (at 23:00: the full-day low).
    d_vol   -- running sum of volume of the current UTC day
               through the current bar (at 23:00: full-day vol).
    corr_gate / new_low_day -- daily flags, True only on the
               23:00 bar of a day where they hold.
    attempt_day -- attempt-day number, on the 23:00 bar only.
    ftd_day -- True only on the 23:00 bar of an FTD day.
    ftd_attempt_low -- attempt_low on an FTD bar, NaN elsewhere.
    atr14   -- Wilder ATR(14) for risk.

No lookahead: daily aggregates use only bars up to the current
one; the state machine reads daily values in order; the FTD
test is evaluated only on the completed (23:00) bar.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CORR_DROP = 0.08
LOOKBACK_DAYS = 20
GAIN_PCT = 0.015
ATTEMPT_LO = 4
ATTEMPT_HI = 7
ATR_N = 14


def add_indicators(
    df: pd.DataFrame,
    gain_pct: float = GAIN_PCT,
    attempt_lo: int = ATTEMPT_LO,
    attempt_hi: int = ATTEMPT_HI,
    corr_drop: float = CORR_DROP,
    lookback_days: int = LOOKBACK_DAYS,
    atr_n: int = ATR_N,
) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    empty = {
        "d_close": pd.Series(dtype=float),
        "d_low": pd.Series(dtype=float),
        "d_vol": pd.Series(dtype=float),
        "corr_gate": pd.Series(dtype=bool),
        "new_low_day": pd.Series(dtype=bool),
        "attempt_day": pd.Series(dtype=int),
        "ftd_day": pd.Series(dtype=bool),
        "ftd_attempt_low": pd.Series(dtype=float),
        "atr14": pd.Series(dtype=float),
    }
    if n == 0:
        for k, v in empty.items():
            df[k] = v
        return df

    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    hour = ts.dt.hour.to_numpy(int)
    days = ts.dt.floor("D")
    day_codes, _ = pd.factorize(days, sort=True)
    n_days = int(day_codes.max()) + 1

    c = df["c"].to_numpy(float)
    l = df["l"].to_numpy(float)
    v = df["v"].to_numpy(float)

    # --- daily aggregates -------------------------------------------------
    dc = np.full(n_days, np.nan)
    dl = np.full(n_days, np.nan)
    dv = np.full(n_days, np.nan)
    last_bar = np.full(n_days, -1, dtype=int)
    last_hour = np.full(n_days, -1, dtype=int)
    for j in range(n_days):
        idx = np.where(day_codes == j)[0]
        last_bar[j] = idx[-1]
        last_hour[j] = hour[idx[-1]]
        dc[j] = c[idx[-1]]
        dl[j] = l[idx].min()
        dv[j] = v[idx].sum()

    dc_s = pd.Series(dc)
    dl_s = pd.Series(dl)
    dv_s = pd.Series(dv)
    max_close = dc_s.rolling(lookback_days, min_periods=lookback_days).max()
    min_low_prior = dl_s.shift(1).rolling(lookback_days, min_periods=lookback_days).min()
    corr = (dc_s <= (1.0 - corr_drop) * max_close).fillna(False).to_numpy(bool)
    newlow = (dl_s <= min_low_prior).fillna(False).to_numpy(bool)
    day_ret = (dc_s / dc_s.shift(1) - 1).fillna(0.0).to_numpy(float)
    vol_up = (dv_s > dv_s.shift(1)).fillna(False).to_numpy(bool)

    # --- daily state machine ----------------------------------------------
    ftd = np.zeros(n_days, dtype=bool)
    ftd_low = np.full(n_days, np.nan)
    attempt_day_col = np.zeros(n_days, dtype=int)
    in_attempt = False
    attempt_day = 0
    attempt_low = np.nan
    awaiting = False
    awaiting_low = np.nan
    for j in range(n_days):
        if in_attempt:
            attempt_day += 1
            attempt_day_col[j] = attempt_day
            if dl[j] < attempt_low:
                # Undercut: attempt fails. The undercutting day
                # is itself a new 20-day low; it becomes a fresh
                # awaiting low if the correction is still on.
                in_attempt = False
                attempt_day = 0
                awaiting_low = dl[j]
                awaiting = bool(corr[j])
            elif attempt_day > attempt_hi:
                in_attempt = False
                attempt_day = 0
            elif (
                attempt_lo <= attempt_day <= attempt_hi
                and day_ret[j] >= gain_pct
                and vol_up[j]
            ):
                ftd[j] = True
                ftd_low[j] = attempt_low
                in_attempt = False
                attempt_day = 0
        else:
            if newlow[j]:
                awaiting_low = dl[j]
                if corr[j]:
                    awaiting = True
            elif awaiting and j >= 1 and dc[j] > dc[j - 1]:
                in_attempt = True
                attempt_day = 1
                attempt_day_col[j] = 1
                attempt_low = awaiting_low
                awaiting = False

    # --- map daily state back onto 1h bars --------------------------------
    d_close = np.full(n, np.nan)
    d_low_run = np.empty(n)
    d_vol_run = np.empty(n)
    corr_bar = np.zeros(n, dtype=bool)
    newlow_bar = np.zeros(n, dtype=bool)
    attempt_day_bar = np.zeros(n, dtype=int)
    ftd_bar = np.zeros(n, dtype=bool)
    ftd_attempt_low_bar = np.full(n, np.nan)

    cur_min = np.inf
    cur_vol = 0.0
    prev_code = -1
    for i in range(n):
        if day_codes[i] != prev_code:
            cur_min = np.inf
            cur_vol = 0.0
            prev_code = day_codes[i]
        cur_min = min(cur_min, l[i])
        cur_vol += v[i]
        d_low_run[i] = cur_min
        d_vol_run[i] = cur_vol

    for j in range(n_days):
        idx = np.where(day_codes == j)[0]
        last = last_bar[j]
        prev_close = dc[j - 1] if j >= 1 else np.nan
        if last_hour[j] == 23:
            d_close[last] = dc[j]
            d_close[idx[:-1]] = prev_close
            corr_bar[last] = corr[j]
            newlow_bar[last] = newlow[j]
            attempt_day_bar[last] = attempt_day_col[j]
            ftd_bar[last] = ftd[j]
            ftd_attempt_low_bar[last] = ftd_low[j]
        else:
            # Incomplete day: nothing is final yet; keep the
            # prior completed day's close.
            d_close[idx] = prev_close

    df["d_close"] = d_close
    df["d_low"] = d_low_run
    df["d_vol"] = d_vol_run
    df["corr_gate"] = corr_bar
    df["new_low_day"] = newlow_bar
    df["attempt_day"] = attempt_day_bar
    df["ftd_day"] = ftd_bar
    df["ftd_attempt_low"] = ftd_attempt_low_bar
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
