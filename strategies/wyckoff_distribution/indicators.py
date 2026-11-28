"""Wyckoff distribution indicators (SHORT ONLY).

The bearish mirror of strategies/wyckoff_accumulation, with
every element inverted. Read that module first; the machinery
below is the same state machine with the signs flipped.

    range_high_120 / range_low_120 -- trailing 120-bar high/low
    advance_gate -- close 120 bars ago <= 95% of the current
                    close (price advanced >= 5% over 120 bars);
                    gates the UTAD
    atr14, vol_sma20 -- Wilder ATR(14), volume SMA(20)
    climax -- buying climax (BC): bar range > 2x ATR(14) AND
              the close in the upper 25% of its own range AND
              volume > 1.5x vol-SMA(20). Recorded as a
              diagnostic anchor; the entry chain below does
              not require it (the range edges are the trailing
              120-bar high/low regardless).
    utad -- upthrust-after-distribution bar: the high poked
            above the trailing 120-bar high (measured against
            the range high BEFORE the poke bar, since the
            current bar's high is part of the rolling window)
            and the close reclaimed back below that frozen
            poke level within 3 bars (same-bar reclaim
            allowed). A higher high while waiting re-anchors
            the poke (new 3-bar clock, higher utad_high).
    utad_high -- highest high of the poke, carried forward
                 from the most recent confirmed UTAD (NaN
                 before the first UTAD)
    sow -- sign of weakness: after a UTAD (within the last 48
           bars), a wide down bar: close below the range
           midpoint AND bar range > 1.5x ATR AND volume >
           1.2x vol-SMA(20). First such bar per UTAD only.
    lpsy -- last point of supply: after an SOW (within 24
            bars), the first bar whose high holds below
            utad_high and whose close is below range_high (a
            lower-high pullback). First such bar per SOW only.

All single-fire state-machine events: a UTAD, SOW, or LPSY
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
ADVANCE_PCT = 0.05
CLIMAX_RANGE_MULT = 2.0
CLIMAX_VOL_MULT = 1.5
UTAD_RECLAIM_BARS = 3
SOW_WINDOW = 48
SOW_RANGE_MULT = 1.5
SOW_VOL_MULT = 1.2
LPSY_WINDOW = 24


def add_indicators(
    df: pd.DataFrame,
    range_n: int = RANGE_N,
    atr_n: int = ATR_N,
    vol_n: int = VOL_N,
    advance_pct: float = ADVANCE_PCT,
    climax_range_mult: float = CLIMAX_RANGE_MULT,
    climax_vol_mult: float = CLIMAX_VOL_MULT,
    utad_reclaim_bars: int = UTAD_RECLAIM_BARS,
    sow_window: int = SOW_WINDOW,
    sow_range_mult: float = SOW_RANGE_MULT,
    sow_vol_mult: float = SOW_VOL_MULT,
    lpsy_window: int = LPSY_WINDOW,
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
    # Prior range high: the trailing range high BEFORE the
    # current bar (the current bar's high is part of the
    # rolling window, so h[i] > rh[i] could never be true).
    rh_prev = np.full(n, np.nan)
    rh_prev[1:] = rh_v[:-1]
    advance_gate = np.zeros(n, dtype=bool)
    for i in range(range_n, n):
        if c[i] > 0 and c[i - range_n] <= (1.0 - advance_pct) * c[i]:
            advance_gate[i] = True
    df["advance_gate"] = advance_gate

    climax = np.zeros(n, dtype=bool)
    for i in range(n):
        if np.isnan(atr[i]) or np.isnan(vsma[i]):
            continue
        bar_range = h[i] - l[i]
        if (
            bar_range > climax_range_mult * atr[i]
            and c[i] >= h[i] - 0.25 * bar_range
            and v[i] > climax_vol_mult * vsma[i]
        ):
            climax[i] = True
    df["climax"] = climax

    utad = np.zeros(n, dtype=bool)
    utad_high_col = np.full(n, np.nan)
    sow = np.zeros(n, dtype=bool)
    lpsy = np.zeros(n, dtype=bool)

    # State machine (mirror of the accumulation spring machine).
    poke_level = np.nan   # frozen range high the poke broke above
    poke_bar = -1         # bar of the (latest) poke high
    poke_high = np.nan    # highest high since the poke started
    utad_bar = -1         # bar of the last confirmed UTAD
    cur_utad_high = np.nan
    sow_armed = False     # a UTAD confirmed, SOW not yet seen
    sow_bar = -1          # bar of the last SOW
    lpsy_armed = False    # an SOW seen, LPSY not yet seen

    for i in range(n):
        # --- UTAD: poke above the prior range high, reclaim within 3 bars
        if not np.isnan(rh_prev[i]):
            if np.isnan(poke_level):
                if h[i] > rh_prev[i] and advance_gate[i]:
                    poke_level = rh_prev[i]
                    poke_bar = i
                    poke_high = h[i]
            else:
                if h[i] > poke_high:
                    # Higher high while waiting: re-anchor.
                    poke_high = h[i]
                    poke_bar = i
                if i - poke_bar > utad_reclaim_bars:
                    poke_level = np.nan
                    poke_bar = -1
        if not np.isnan(poke_level) and c[i] < poke_level:
            # Reclaim: UTAD confirmed on this bar.
            utad[i] = True
            utad_bar = i
            cur_utad_high = poke_high
            sow_armed = True
            sow_bar = -1
            lpsy_armed = False
            poke_level = np.nan
            poke_bar = -1
        utad_high_col[i] = cur_utad_high

        # --- SOW: first wide down bar closing below the midpoint,
        #     within 48 bars of the UTAD.
        if (
            sow_armed
            and utad_bar >= 0
            and i - utad_bar <= sow_window
            and not np.isnan(atr[i])
            and not np.isnan(vsma[i])
            and not np.isnan(mid_v[i])
            and c[i] < mid_v[i]
            and (h[i] - l[i]) > sow_range_mult * atr[i]
            and v[i] > sow_vol_mult * vsma[i]
        ):
            sow[i] = True
            sow_bar = i
            sow_armed = False
            lpsy_armed = True
        elif sow_armed and utad_bar >= 0 and i - utad_bar > sow_window:
            sow_armed = False

        # --- LPSY: first bar after the SOW (within 24 bars) whose
        #     high holds below utad_high and close is below the
        #     range high.
        if (
            lpsy_armed
            and sow_bar >= 0
            and i > sow_bar
            and i - sow_bar <= lpsy_window
            and not np.isnan(cur_utad_high)
            and not np.isnan(rh_v[i])
            and h[i] < cur_utad_high
            and c[i] < rh_v[i]
        ):
            lpsy[i] = True
            lpsy_armed = False
        elif lpsy_armed and sow_bar >= 0 and i - sow_bar > lpsy_window:
            lpsy_armed = False

    df["utad"] = utad
    df["utad_high"] = utad_high_col
    df["sow"] = sow
    df["lpsy"] = lpsy
    return df
