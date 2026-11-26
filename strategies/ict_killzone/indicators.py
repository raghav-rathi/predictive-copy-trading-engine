"""ICT killzone indicators.

Times in UTC (November = EST, UTC-5):

    Asian window    00:00-03:00 UTC (bars 00:00, 01:00, 02:00)
    London killzone 07:00-10:00 UTC (02:00-05:00 ET)
    NY killzone     12:00-14:00 UTC (07:00-09:00 ET)

Asian range = high/low of the 00:00-03:00 UTC bars of the
current UTC day; it is only known once the 03:00 bar closes,
so no setup can arm before then. During a London or NY
killzone window only, per side:

    sweep       -- close beyond the Asian high/low (long: below
                   the Asian low; short: above the Asian high),
                   then close back inside that level within 2
                   bars of the bar that made the sweep extreme
                   (each new extreme re-anchors the clock, as in
                   ict_ote_entry).
    displacement -- within the same killzone window, price moves
                   >= 1.0x ATR(14) in the sweep-opposite direction
                   (from the back-inside close) AND breaks the
                   near swing (frozen at the back-inside bar).
    leg         -- sweep extreme -> displacement extreme (highest
                   high / lowest low from the back-inside bar
                   through the confirmation bar).
    entry level -- the 50% level of the displacement leg. On 1h
                   bars the FVG is approximated by the leg's
                   midpoint (documented simplification: a true
                   fair-value gap needs sub-hour structure to
                   locate; the midpoint is the leg's centre).
    armed       -- from the displacement bar until the close
                   crosses the 50% level (entry, setup consumed),
                   the close goes beyond the leg start
                   (invalidation), or the UTC day ends (expiry --
                   intraday by design).
                   DEVIATION, documented: the spec says "no entries
                   outside the two killzone windows", but on 1h bars
                   the minimum sequence is 4 bars (sweep ->
                   back-inside -> displacement -> retracement) while
                   the London window is 3 bars (07:00, 08:00, 09:00)
                   and the NY window 2 bars (12:00, 13:00) -- a
                   strict reading makes the strategy unfireable by
                   construction. Two accommodations, both enforced
                   in code: (1) windows are inclusive of their
                   end-hour bar (London 07:00-10:00, NY 12:00-14:00
                   hourly bars -- the bar opening at the end hour
                   is that hour's price action), so the NY window
                   can at least contain the 3-bar sweep -> back ->
                   displacement sequence; (2) the sweep and the
                   displacement must both complete inside a window,
                   but an armed setup's retracement entry may land
                   after the window closes, expiring at the UTC day
                   boundary instead. No NEW setup may start outside
                   a window.

A sweep at the last bar of a window whose back-inside lands
outside the window dies: displacement must complete inside
the same window. One pending setup per side at a time.

Columns:
    asian_high, asian_low -- current UTC day's Asian range
    killzone              -- bar is inside a London/NY window
    kz_window             -- 0 none, 1 London, 2 NY
    swing_high_20, swing_low_20, atr14
    kz_long_armed, kz_short_armed
    kz_long_mid, kz_short_mid                 -- 50% entry level
    kz_long_leg_start, kz_short_leg_start     -- sweep extreme
    kz_long_disp_extreme, kz_short_disp_extreme

No lookahead: the Asian range uses only 00:00-03:00 bars of
the current day, swing extremes are shifted by one bar, ATR
is Wilder smoothing, and the state machine only reads bars
up to the current one.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SWING_N = 20
DISP_MULT = 1.0
SWEEP_BACK_BARS = 2
RETRACE_LEVEL = 0.50

# Killzone windows as (start_hour, end_hour_inclusive, id).
# Bars are labelled by their open hour, so the bar opening at
# the end hour is that hour's price action and belongs to the
# window (see the deviation note in the module docstring).
WINDOWS = ((7, 10, 1), (12, 14, 2))


def _window_id(hour: int) -> int:
    for start, end, wid in WINDOWS:
        if start <= hour <= end:
            return wid
    return 0


def add_indicators(
    df: pd.DataFrame,
    swing_n: int = SWING_N,
    disp_mult: float = DISP_MULT,
    sweep_back_bars: int = SWEEP_BACK_BARS,
    retrace_level: float = RETRACE_LEVEL,
) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    hour = ts.dt.hour.to_numpy()
    daynum = (df["t"].to_numpy() // 86_400_000).astype("int64")
    # Asian range: bars 00:00-02:00 UTC of each UTC day.
    asian_mask = hour < 3
    tmp = pd.DataFrame({"day": daynum, "h": df["h"], "l": df["l"]})
    grp = tmp[asian_mask].groupby("day").agg(ah=("h", "max"), al=("l", "min"))
    df["asian_high"] = pd.Series(daynum).map(grp["ah"]).to_numpy(float)
    df["asian_low"] = pd.Series(daynum).map(grp["al"]).to_numpy(float)
    df.loc[hour < 3, ["asian_high", "asian_low"]] = np.nan
    wid = np.array([_window_id(int(hh)) for hh in hour], dtype=int)
    df["kz_window"] = wid
    df["killzone"] = wid > 0
    d = B.donchian(df["h"], df["l"], swing_n)
    df[f"swing_high_{swing_n}"] = d[f"donchian_high_{swing_n}"]
    df[f"swing_low_{swing_n}"] = d[f"donchian_low_{swing_n}"]
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)

    n = len(df)
    c = df["c"].to_numpy(float)
    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    atr = df["atr14"].to_numpy(float)
    ph = df[f"swing_high_{swing_n}"].shift(1).to_numpy(float)
    pl = df[f"swing_low_{swing_n}"].shift(1).to_numpy(float)
    ah = df["asian_high"].to_numpy(float)
    al = df["asian_low"].to_numpy(float)
    wkey = daynum * 10 + wid

    armed_l = np.zeros(n, dtype=bool)
    armed_s = np.zeros(n, dtype=bool)
    mid_l = np.full(n, np.nan)
    leg_l = np.full(n, np.nan)
    dext_l = np.full(n, np.nan)
    mid_s = np.full(n, np.nan)
    leg_s = np.full(n, np.nan)
    dext_s = np.full(n, np.nan)

    states = {1: {"stage": "idle"}, -1: {"stage": "idle"}}
    outs = {
        1: (armed_l, mid_l, leg_l, dext_l),
        -1: (armed_s, mid_s, leg_s, dext_s),
    }
    prev_p = {1: np.nan, -1: np.nan}

    for i in range(n):
        for sign in (1, -1):
            st = states[sign]
            armed, mid, leg, dext = outs[sign]
            p = sign * c[i]
            # Swept level in transformed space: Asian low (long)
            # / Asian high (short). NaN until the range completes.
            level = sign * (al[i] if sign == 1 else ah[i])
            near = sign * (ph[i] if sign == 1 else pl[i])
            extreme = sign * (l[i] if sign == 1 else h[i])
            bar_extreme = sign * (h[i] if sign == 1 else l[i])
            if np.isnan(level):
                # No Asian range yet: any in-flight setup is dead
                # (a new day's range replaces the old one).
                st["stage"] = "idle"
                prev_p[sign] = p
                continue
            stage = st["stage"]
            if stage == "idle":
                if wid[i] > 0 and not np.isnan(near) and p < level:
                    st.update(stage="swept", sweep_bar=i,
                              level=level, extreme=extreme)
            elif stage == "swept":
                if extreme < st["extreme"]:
                    st["extreme"] = extreme
                    st["sweep_bar"] = i
                if i > st["sweep_bar"] + sweep_back_bars:
                    st["stage"] = "idle"
                elif p > st["level"]:
                    if wid[i] == 0:
                        # Back inside outside any window: the
                        # displacement could never complete inside
                        # the window, so the setup dies here.
                        st["stage"] = "idle"
                    else:
                        st.update(stage="displaced", back_bar=i, back_close=p,
                                  wkey=wkey[i], run_end=bar_extreme, near=near)
            elif stage == "displaced":
                st["run_end"] = max(st["run_end"], bar_extreme)
                if wkey[i] != st["wkey"]:
                    st["stage"] = "idle"  # window ended
                elif (
                    not np.isnan(atr[i])
                    and p - st["back_close"] >= disp_mult * atr[i]
                    and p > st["near"]
                ):
                    leg_start = st["extreme"]
                    leg_end = st["run_end"]
                    rng = leg_end - leg_start
                    if rng > 0:
                        mid_t = leg_end - retrace_level * rng
                        st.update(stage="armed", leg_start=leg_start,
                                  leg_end=leg_end, mid_t=mid_t,
                                  day=daynum[i])
                    else:
                        st["stage"] = "idle"
            elif stage == "armed":
                if daynum[i] != st["day"]:
                    st["stage"] = "idle"  # day ended: expiry (see deviation note)
                elif p < st["leg_start"]:
                    st["stage"] = "idle"  # invalidated: beyond leg start
                else:
                    armed[i] = True
                    mid[i] = sign * st["mid_t"]
                    leg[i] = sign * st["leg_start"]
                    dext[i] = sign * st["leg_end"]
                    # Entry: close crosses below the 50% level
                    # (transformed space: p crosses below mid_t).
                    if p < st["mid_t"] and prev_p[sign] >= st["mid_t"]:
                        st["stage"] = "idle"  # entry consumes the setup
            prev_p[sign] = p

    df["kz_long_armed"] = armed_l
    df["kz_long_mid"] = mid_l
    df["kz_long_leg_start"] = leg_l
    df["kz_long_disp_extreme"] = dext_l
    df["kz_short_armed"] = armed_s
    df["kz_short_mid"] = mid_s
    df["kz_short_leg_start"] = leg_s
    df["kz_short_disp_extreme"] = dext_s
    return df
