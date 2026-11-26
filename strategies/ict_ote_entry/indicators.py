"""ICT Optimal Trade Entry (OTE) indicators.

State machine over bars (causal only), per side:

    sweep       -- close beyond the prior 20-bar swing extreme
                   (long: below the prior 20-bar low; short: above
                   the prior 20-bar high), then close back inside
                   that level within 3 bars of the bar that made
                   the sweep extreme (each new extreme re-anchors
                   the clock -- while price keeps extending, the
                   sweep is still in flight).
    displacement -- within the next 6 bars, price moves >= 1.5x
                   ATR(14) in the sweep-opposite direction (measured
                   from the back-inside close) AND breaks the near
                   swing (long: close above the prior 20-bar high;
                   short: close below the prior 20-bar low), with
                   the near swing frozen at the back-inside bar --
                   a rolling level would absorb the displacement
                   itself and a gradual move could never break it.
    leg         -- sweep extreme -> displacement extreme (highest
                   high / lowest low from the back-inside bar
                   through the confirmation bar).
    OTE zone    -- 62-79% retracement of the leg, measured from the
                   displacement extreme back toward the sweep
                   extreme; 70.5% midline carried as a diagnostic.
    armed       -- from the displacement bar until the close enters
                   the zone (entry, setup consumed), the close goes
                   beyond 100% of the leg (beyond the sweep extreme
                   -- invalidation), or 24 bars pass without a touch
                   (expiry).

One pending setup per side at a time; a new sweep is ignored
while a setup is in flight. The zone is fixed at the
displacement-confirmation bar: if price extends beyond the
displacement extreme while armed, the zone is NOT redrawn
(documented simplification -- the leg end is the extreme
through confirmation, not the eventual swing extreme).

Columns:
    swing_high_20, swing_low_20 -- prior-window swing extremes
    atr14                        -- ATR(14), diagnostic + displacement yardstick
    ote_long_armed, ote_short_armed
    ote_long_zone_lo/hi/mid, ote_short_zone_lo/hi/mid
    ote_long_leg_start, ote_short_leg_start   -- sweep extreme (100% level)
    ote_long_disp_extreme, ote_short_disp_extreme

No lookahead: swing extremes are shifted by one bar, ATR is
Wilder smoothing, and the state machine only reads bars up
to the current one. base.rsi is not used here; the ATR note
in the house rules (rsi 0-fill on flat stretches) does not
apply.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SWING_N = 20
DISP_MULT = 1.5
SWEEP_BACK_BARS = 3
DISP_BARS = 6
OTE_LO = 0.62
OTE_HI = 0.79
OTE_MID = 0.705
EXPIRY_BARS = 24


def add_indicators(
    df: pd.DataFrame,
    swing_n: int = SWING_N,
    disp_mult: float = DISP_MULT,
    sweep_back_bars: int = SWEEP_BACK_BARS,
    disp_bars: int = DISP_BARS,
    ote_lo: float = OTE_LO,
    ote_hi: float = OTE_HI,
    expiry_bars: int = EXPIRY_BARS,
) -> pd.DataFrame:
    df = df.copy()
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

    armed_l = np.zeros(n, dtype=bool)
    armed_s = np.zeros(n, dtype=bool)
    zlo_l = np.full(n, np.nan)
    zhi_l = np.full(n, np.nan)
    zmid_l = np.full(n, np.nan)
    leg_l = np.full(n, np.nan)
    dext_l = np.full(n, np.nan)
    zlo_s = np.full(n, np.nan)
    zhi_s = np.full(n, np.nan)
    zmid_s = np.full(n, np.nan)
    leg_s = np.full(n, np.nan)
    dext_s = np.full(n, np.nan)

    # Per-side state. Prices are carried in "transformed" space
    # p = sign * price with sign +1 (long) / -1 (short), so one
    # code path serves both sides: a sweep is p below the swept
    # level, displacement is p rising, the leg runs upward, and
    # invalidation is p below the leg start.
    states = {
        1: {"stage": "idle"},
        -1: {"stage": "idle"},
    }
    outs = {
        1: (armed_l, zlo_l, zhi_l, zmid_l, leg_l, dext_l),
        -1: (armed_s, zlo_s, zhi_s, zmid_s, leg_s, dext_s),
    }

    for i in range(n):
        for sign in (1, -1):
            st = states[sign]
            armed, zlo, zhi, zmid, leg, dext = outs[sign]
            p = sign * c[i]
            # Swept level / near-swing level in transformed space.
            level = sign * (pl[i] if sign == 1 else ph[i])
            near = sign * (ph[i] if sign == 1 else pl[i])
            extreme = sign * (l[i] if sign == 1 else h[i])
            bar_extreme = sign * (h[i] if sign == 1 else l[i])
            if np.isnan(level) or np.isnan(near):
                continue
            stage = st["stage"]
            if stage == "idle":
                if p < level:
                    st.update(stage="swept", sweep_bar=i,
                              level=level, extreme=extreme)
            elif stage == "swept":
                # The sweep extreme is the furthest price reached
                # while the sweep is in flight, not just the first
                # sweep bar's low/high. The 3-bar back-inside clock
                # runs from the bar that made the sweep extreme:
                # while price keeps extending the sweep it is still
                # sweeping, so each new extreme re-anchors the
                # deadline. "Back inside" is judged against the
                # level swept at the sweep bar (stored), not the
                # current bar's swing level, which has already
                # absorbed the dip.
                if extreme < st["extreme"]:
                    st["extreme"] = extreme
                    st["sweep_bar"] = i
                if i > st["sweep_bar"] + sweep_back_bars:
                    st["stage"] = "idle"
                elif p > st["level"]:
                    # Freeze the near swing at the back-inside bar:
                    # a rolling high would absorb the displacement
                    # itself, so a gradual move could never break
                    # it. The level to break is the swing as it
                    # stood when the displacement began.
                    st.update(stage="displaced", back_bar=i, back_close=p,
                              deadline=i + disp_bars, run_end=bar_extreme,
                              near=near)
            elif stage == "displaced":
                st["run_end"] = max(st["run_end"], bar_extreme)
                if i > st["deadline"]:
                    st["stage"] = "idle"
                elif (
                    not np.isnan(atr[i])
                    and p - st["back_close"] >= disp_mult * atr[i]
                    and p > st["near"]
                ):
                    leg_start = st["extreme"]
                    leg_end = st["run_end"]
                    rng = leg_end - leg_start
                    if rng > 0:
                        lo_t = leg_end - ote_hi * rng
                        hi_t = leg_end - ote_lo * rng
                        mid_t = leg_end - OTE_MID * rng
                        st.update(stage="armed", leg_start=leg_start,
                                  leg_end=leg_end, lo_t=lo_t, hi_t=hi_t,
                                  mid_t=mid_t, disp_bar=i,
                                  expiry=i + expiry_bars)
                    else:
                        st["stage"] = "idle"
            elif stage == "armed":
                if i > st["expiry"]:
                    st["stage"] = "idle"
                elif p < st["leg_start"]:
                    st["stage"] = "idle"  # invalidated: beyond 100%
                elif lo_t_in_zone(st, p):
                    armed[i] = True
                    zlo[i], zhi[i] = _zone_actual(sign, st["lo_t"], st["hi_t"])
                    zmid[i] = sign * st["mid_t"]
                    leg[i] = sign * st["leg_start"]
                    dext[i] = sign * st["leg_end"]
                    st["stage"] = "idle"  # entry consumes the setup
                else:
                    armed[i] = True
                    zlo[i], zhi[i] = _zone_actual(sign, st["lo_t"], st["hi_t"])
                    zmid[i] = sign * st["mid_t"]
                    leg[i] = sign * st["leg_start"]
                    dext[i] = sign * st["leg_end"]

    df["ote_long_armed"] = armed_l
    df["ote_long_zone_lo"] = zlo_l
    df["ote_long_zone_hi"] = zhi_l
    df["ote_long_zone_mid"] = zmid_l
    df["ote_long_leg_start"] = leg_l
    df["ote_long_disp_extreme"] = dext_l
    df["ote_short_armed"] = armed_s
    df["ote_short_zone_lo"] = zlo_s
    df["ote_short_zone_hi"] = zhi_s
    df["ote_short_zone_mid"] = zmid_s
    df["ote_short_leg_start"] = leg_s
    df["ote_short_disp_extreme"] = dext_s
    return df


def lo_t_in_zone(st: dict, p: float) -> bool:
    return st["lo_t"] <= p <= st["hi_t"]


def _zone_actual(sign: int, lo_t: float, hi_t: float):
    """Transformed-space zone bounds back to actual prices."""
    a, b = sign * lo_t, sign * hi_t
    return (min(a, b), max(a, b))
