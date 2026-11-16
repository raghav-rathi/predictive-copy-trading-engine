"""Dow Theory trend signals.

Trend is read off confirmed swing structure, not averages:

    uptrend   -- higher highs AND higher lows (HH + HL)
    downtrend -- lower highs AND lower lows (LH + LL)

    long_entry  -- uptrend confirmed, price pulled back 33-66% of the
                   last up-leg (last swing high minus the swing low
                   that preceded it), then a 1h close breaks above
                   the last swing high with volume above its 20-bar
                   mean
    short_entry -- mirror image
    long_exit   -- structure breaks: a new swing low under the previous
                   swing low (lower low in an uptrend), or the close
                   retraces more than 66% of the last up-leg
    short_exit  -- mirror image

The pullback is measured against the *frozen* leg that formed the
last swing extreme (the range is fixed when the pivot confirms), so
the pullback's own swing low confirming does not reset the range
and disarm the setup mid-pullback.

Volume confirmation is the single-asset substitute for Dow's
cross-average confirmation: the breakout bar must print volume above
its 20-bar mean (vol_ratio > 1).

The state machine walks the confirmed pivots in order; every decision
on bar i uses pivots/closes through bar i only, and the harness
executes at bar i+1's open, so there is no lookahead.
"""

import numpy as np
import pandas as pd

RETR_LO = 0.33   # shipped pullback band, lower edge
RETR_HI = 0.66   # shipped pullback band, upper edge (also the exit line)
VOL_MIN = 1.0    # shipped: breakout volume must beat its 20-bar mean


def _dow_state(df: pd.DataFrame) -> pd.DataFrame:
    """Walk the pivots; return per-bar trend / pullback / armed state."""
    n = len(df)
    sh = df["swing_high"].to_numpy(dtype=float)
    sl = df["swing_low"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)

    trend = np.zeros(n, dtype=int)
    armed_long = np.zeros(n, dtype=bool)
    armed_short = np.zeros(n, dtype=bool)
    retr = np.full(n, np.nan)  # current pullback depth of the active leg
    leg_hi = np.full(n, np.nan)   # last swing high (long breakout level)
    leg_lo = np.full(n, np.nan)   # swing low that preceded it
    dleg_hi = np.full(n, np.nan)  # swing high that preceded the last low
    dleg_lo = np.full(n, np.nan)  # last swing low (short breakout level)

    last_sh = np.nan
    prev_sh = np.nan
    last_sl = np.nan
    prev_sl = np.nan
    tr = 0
    # frozen legs: fixed when the extreme pivot confirms
    up_hi = np.nan
    up_lo = np.nan
    dn_hi = np.nan
    dn_lo = np.nan
    pb_min = np.nan  # lowest close since the last swing high
    pb_max = np.nan  # highest close since the last swing low
    arm_l = False
    arm_s = False

    def _refresh_trend():
        nonlocal tr
        if (not np.isnan(prev_sh) and not np.isnan(last_sh)
                and not np.isnan(prev_sl) and not np.isnan(last_sl)):
            if last_sh > prev_sh and last_sl > prev_sl:
                tr = 1
            elif last_sh < prev_sh and last_sl < prev_sl:
                tr = -1

    for i in range(n):
        if not np.isnan(sh[i]):
            if not np.isnan(last_sh):
                prev_sh = last_sh
            last_sh = sh[i]
            _refresh_trend()
            # freeze the up-leg: this high + the swing low before it
            up_hi = sh[i]
            up_lo = last_sl
            pb_min = np.nan  # new swing high restarts the pullback clock
            arm_l = False
        if not np.isnan(sl[i]):
            if not np.isnan(last_sl):
                prev_sl = last_sl
            last_sl = sl[i]
            _refresh_trend()
            # freeze the down-leg: this low + the swing high before it
            dn_lo = sl[i]
            dn_hi = last_sh
            pb_max = np.nan
            arm_s = False

        # pullback depth vs the frozen leg
        if tr == 1 and not np.isnan(up_hi) and not np.isnan(up_lo) \
                and up_hi > up_lo:
            pb_min = c[i] if np.isnan(pb_min) else min(pb_min, c[i])
            depth = (up_hi - pb_min) / (up_hi - up_lo)
            retr[i] = depth
            arm_l = RETR_LO <= depth <= RETR_HI
        elif tr == -1 and not np.isnan(dn_hi) and not np.isnan(dn_lo) \
                and dn_hi > dn_lo:
            pb_max = c[i] if np.isnan(pb_max) else max(pb_max, c[i])
            depth = (pb_max - dn_lo) / (dn_hi - dn_lo)
            retr[i] = depth
            arm_s = RETR_LO <= depth <= RETR_HI

        trend[i] = tr
        armed_long[i] = arm_l
        armed_short[i] = arm_s
        leg_hi[i] = up_hi
        leg_lo[i] = up_lo
        dleg_hi[i] = dn_hi
        dleg_lo[i] = dn_lo

    return pd.DataFrame(
        {"trend": trend, "armed_long": armed_long,
         "armed_short": armed_short, "pullback_depth": retr,
         "leg_hi": leg_hi, "leg_lo": leg_lo,
         "dleg_hi": dleg_hi, "dleg_lo": dleg_lo}, index=df.index)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    st = _dow_state(df)
    for col in st.columns:
        df[col] = st[col]

    c = df["c"]
    sh = df["swing_high"]
    sl = df["swing_low"]
    vr = df["vol_ratio"]
    tr = df["trend"]

    # --- entries: breakout of the last swing extreme after an armed pullback
    long_entry = (
        (tr == 1) & df["armed_long"]
        & (c > df["leg_hi"]) & (vr > VOL_MIN)
    ).fillna(False)
    short_entry = (
        (tr == -1) & df["armed_short"]
        & (c < df["dleg_lo"]) & (vr > VOL_MIN)
    ).fillna(False)

    # --- exits: structure break, or retracement past 66% of the leg
    # A lower low is detected when a fresh swing low prints below the
    # previous swing low; the exit fires on the confirmation bar.
    prev_sl_series = sl.ffill().shift(1)
    new_ll = sl.notna() & (sl < prev_sl_series)
    prev_sh_series = sh.ffill().shift(1)
    new_hh = sh.notna() & (sh > prev_sh_series)
    up_range = df["leg_hi"] - df["leg_lo"]
    dn_range = df["dleg_hi"] - df["dleg_lo"]
    deep_long = (c < df["leg_hi"] - RETR_HI * up_range).fillna(False)
    deep_short = (c > df["dleg_lo"] + RETR_HI * dn_range).fillna(False)

    long_exit = ((tr == -1) | new_ll | deep_long).fillna(False)
    short_exit = ((tr == 1) | new_hh | deep_short).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
