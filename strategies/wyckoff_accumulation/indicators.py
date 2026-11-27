"""Wyckoff accumulation indicators (LONG ONLY).

    range_high_120 / range_low_120 -- trailing 120-bar high/low
    decline_gate -- close 120 bars ago >= 5% above the current
                    close (the schematic only exists after a
                    decline); gates the spring
    atr14, vol_sma20 -- Wilder ATR(14), volume SMA(20)
    climax -- selling climax: bar range > 2x ATR(14) AND the
              close in the lower 25% of its own range AND
              volume > 1.5x vol-SMA(20). Recorded as a
              diagnostic anchor; the entry chain below does
              not require it (the range edges are the trailing
              120-bar high/low regardless).
    spring -- spring-reclaim bar: the low dipped below the
              trailing 120-bar low (measured against the range
              low BEFORE the dip bar, since the current bar's
              low is part of the rolling window) and the close
              reclaimed back above that frozen dip level within
              3 bars (same-bar reclaim allowed). A lower low
              while waiting re-anchors the dip (new 3-bar
              clock, deeper spring_low).
    spring_low -- lowest low of the dip, carried forward from
              the most recent confirmed spring (NaN before the
              first spring)
    sos -- sign of strength: after a spring (within the last 48
           bars), a wide up bar: close above the range
           midpoint AND bar range > 1.5x ATR AND volume >
           1.2x vol-SMA(20). First such bar per spring only.
    lps -- last point of support: after an SOS (within 24
           bars), the first bar whose low holds above
           spring_low and whose close is above range_low (a
           higher-low pullback). First such bar per SOS only.

All single-fire state-machine events: a spring, SOS, or LPS
fires on exactly one bar per setup, so entries cannot
re-fire while a level condition persists. All columns are
causal (rolling windows, shifted prior range, Wilder ATR);
the state machine only reads bars up to the current one.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RANGE_N = 120
ATR_N = 14
VOL_N = 20
DECLINE_PCT = 0.05
CLIMAX_RANGE_MULT = 2.0
CLIMAX_VOL_MULT = 1.5
SPRING_RECLAIM_BARS = 3
SOS_WINDOW = 48
SOS_RANGE_MULT = 1.5
SOS_VOL_MULT = 1.2
LPS_WINDOW = 24


def add_indicators(
    df: pd.DataFrame,
    range_n: int = RANGE_N,
    atr_n: int = ATR_N,
    vol_n: int = VOL_N,
    decline_pct: float = DECLINE_PCT,
    climax_range_mult: float = CLIMAX_RANGE_MULT,
    climax_vol_mult: float = CLIMAX_VOL_MULT,
    spring_reclaim_bars: int = SPRING_RECLAIM_BARS,
    sos_window: int = SOS_WINDOW,
    sos_range_mult: float = SOS_RANGE_MULT,
    sos_vol_mult: float = SOS_VOL_MULT,
    lps_window: int = LPS_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    rh = df["h"].rolling(range_n, min_periods=range_n).max()
    rl = df["l"].rolling(range_n, min_periods=range_n).min()
    df["range_high_120"] = rh
    df["range_low_120"] = rl
    df["range_mid_120"] = rl + 0.5 * (rh - rl)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["vol_sma20"] = B.sma(df["v"], vol_n)
    c = df["c"].to_numpy(float)
    h = df["h"].to_numpy(float)
    l = df["l"].to_numpy(float)
    v = df["v"].to_numpy(float)
    atr = df["atr14"].to_numpy(float)
    vsma = df["vol_sma20"].to_numpy(float)
    rh_v = rh.to_numpy(float)
    rl_v = rl.to_numpy(float)
    mid_v = df["range_mid_120"].to_numpy(float)
    # Prior range low: the trailing range low BEFORE the current
    # bar (the current bar's low is part of the rolling window,
    # so l[i] < rl[i] could never be true).
    rl_prev = np.full(n, np.nan)
    rl_prev[1:] = rl_v[:-1]
    decline_gate = np.zeros(n, dtype=bool)
    for i in range(range_n, n):
        if c[i] > 0 and c[i - range_n] >= (1.0 + decline_pct) * c[i]:
            decline_gate[i] = True
    df["decline_gate"] = decline_gate

    climax = np.zeros(n, dtype=bool)
    for i in range(n):
        if np.isnan(atr[i]) or np.isnan(vsma[i]):
            continue
        bar_range = h[i] - l[i]
        if (
            bar_range > climax_range_mult * atr[i]
            and c[i] <= l[i] + 0.25 * bar_range
            and v[i] > climax_vol_mult * vsma[i]
        ):
            climax[i] = True
    df["climax"] = climax

    spring = np.zeros(n, dtype=bool)
    spring_low_col = np.full(n, np.nan)
    sos = np.zeros(n, dtype=bool)
    lps = np.zeros(n, dtype=bool)

    # State machine.
    dip_level = np.nan    # frozen range low the dip broke below
    dip_bar = -1          # bar of the (latest) dip low
    dip_low = np.nan      # lowest low since the dip started
    spring_bar = -1       # bar of the last confirmed spring
    cur_spring_low = np.nan
    sos_armed = False     # a spring confirmed, SOS not yet seen
    sos_bar = -1          # bar of the last SOS
    lps_armed = False     # an SOS seen, LPS not yet seen

    for i in range(n):
        # --- spring: dip below the prior range low, reclaim within 3 bars
        if not np.isnan(rl_prev[i]):
            if np.isnan(dip_level):
                if l[i] < rl_prev[i] and decline_gate[i]:
                    dip_level = rl_prev[i]
                    dip_bar = i
                    dip_low = l[i]
            else:
                if l[i] < dip_low:
                    # Deeper dip while waiting: re-anchor.
                    dip_low = l[i]
                    dip_bar = i
                if i - dip_bar > spring_reclaim_bars:
                    dip_level = np.nan
                    dip_bar = -1
        if not np.isnan(dip_level) and c[i] > dip_level:
            # Reclaim: spring confirmed on this bar.
            spring[i] = True
            spring_bar = i
            cur_spring_low = dip_low
            sos_armed = True
            sos_bar = -1
            lps_armed = False
            dip_level = np.nan
            dip_bar = -1
        spring_low_col[i] = cur_spring_low

        # --- SOS: first wide up bar closing above the midpoint,
        #     within 48 bars of the spring.
        if (
            sos_armed
            and spring_bar >= 0
            and i - spring_bar <= sos_window
            and not np.isnan(atr[i])
            and not np.isnan(vsma[i])
            and not np.isnan(mid_v[i])
            and c[i] > mid_v[i]
            and (h[i] - l[i]) > sos_range_mult * atr[i]
            and v[i] > sos_vol_mult * vsma[i]
        ):
            sos[i] = True
            sos_bar = i
            sos_armed = False
            lps_armed = True
        elif sos_armed and spring_bar >= 0 and i - spring_bar > sos_window:
            sos_armed = False

        # --- LPS: first bar after the SOS (within 24 bars) whose
        #     low holds above spring_low and close is above the
        #     range low.
        if (
            lps_armed
            and sos_bar >= 0
            and i > sos_bar
            and i - sos_bar <= lps_window
            and not np.isnan(cur_spring_low)
            and not np.isnan(rl_v[i])
            and l[i] > cur_spring_low
            and c[i] > rl_v[i]
        ):
            lps[i] = True
            lps_armed = False
        elif lps_armed and sos_bar >= 0 and i - sos_bar > lps_window:
            lps_armed = False

    df["spring"] = spring
    df["spring_low"] = spring_low_col
    df["sos"] = sos
    df["lps"] = lps
    return df
