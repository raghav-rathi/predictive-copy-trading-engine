"""Volatility Contraction Pattern (VCP, Minervini) indicators.

Causal 5-bar pivots as in sfp (centre+2 confirmation, recorded at
the confirmation bar). A pullback runs from a swing high to the
following swing low; depth = (high - low) / high. A rally runs from
a swing low to the following swing high; depth = (high - low) / low.

Long base: >= 2 successive pullbacks where each pullback is
shallower than the previous (depth[k] < 0.95 * depth[k-1]), each
trough is HIGHER than the previous trough, and mean volume on each
down-leg (bars from the pullback's swing-high centre to its
swing-low centre, inclusive) is lower than on the previous
down-leg. The pivot is the high of the last (tightest)
contraction. The short base is the mirror: successive rallies, each
shallower, each peak LOWER, volume declining; pivot = the low of
the last contraction.

A pullback/rally whose later low/high extends the same starting
pivot updates that leg in place rather than starting a new leg.
Legs with depth <= 0 are not pullbacks/rallies and are ignored.

Columns:
    sma50, sma200   -- trend filter (Stage-2 uptrend proxy)
    pivot_high      -- high of the most recent completed pullback
    pivot_low       -- low of the most recent completed rally
    vcp_valid       -- long base valid (bool)
    vcp_valid_short -- short base valid (bool, extra column)
    vol_ma50        -- SMA(volume, 50) for the breakout-volume test
    atr             -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14
VOL_MA_N = 50
SHRINK = 0.95

INDICATOR_COLS = ["sma50", "sma200", "pivot_high", "pivot_low",
                  "vcp_valid", "vcp_valid_short", "vol_ma50", "atr"]


def _chain_state(legs: list[dict], long_side: bool):
    """Scan a leg list for the VCP chain. Returns (valid, pivot).

    valid is True when the trailing run of qualifying transitions
    covers >= 2 legs. pivot is the starting extreme of the last leg.
    """
    if not legs:
        return False, np.nan
    run = 1
    for k in range(1, len(legs)):
        prev, cur = legs[k - 1], legs[k]
        if long_side:
            ok = (cur["depth"] < SHRINK * prev["depth"]
                  and cur["extreme"] > prev["extreme"]
                  and cur["vol"] < prev["vol"])
        else:
            ok = (cur["depth"] < SHRINK * prev["depth"]
                  and cur["extreme"] < prev["extreme"]
                  and cur["vol"] < prev["vol"])
        run = run + 1 if ok else 1
    pivot = legs[-1]["start"]
    return run >= 2, pivot


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N,
                   vol_n: int = VOL_MA_N) -> pd.DataFrame:
    df = df.copy()
    hv = df["h"].to_numpy(dtype=float)
    lv = df["l"].to_numpy(dtype=float)
    vv = df["v"].to_numpy(dtype=float)
    n = len(hv)
    cumv = np.concatenate([[0.0], np.cumsum(vv)])

    def leg_vol(a: int, b: int) -> float:
        return (cumv[b + 1] - cumv[a]) / (b - a + 1)

    sh = np.full(n, np.nan)
    sl = np.full(n, np.nan)
    pivot_high = np.full(n, np.nan)
    pivot_low = np.full(n, np.nan)
    valid_long = np.zeros(n, dtype=bool)
    valid_short = np.zeros(n, dtype=bool)
    highs: list[tuple[int, float]] = []
    lows: list[tuple[int, float]] = []
    pullbacks: list[dict] = []  # start=high, extreme=trough low
    rallies: list[dict] = []    # start=low, extreme=peak high
    cur_h = np.nan
    cur_l = np.nan
    cur_ph = np.nan
    cur_pl = np.nan
    cur_vl = False
    cur_vs = False
    for i in range(n):
        j = i - 2
        new_high = False
        new_low = False
        if j >= 2:
            if (hv[j] > hv[j - 1] and hv[j] > hv[j - 2]
                    and hv[j] >= hv[j + 1] and hv[j] >= hv[j + 2]):
                cur_h = hv[j]
                highs.append((j, hv[j]))
                new_high = True
            if (lv[j] < lv[j - 1] and lv[j] < lv[j - 2]
                    and lv[j] <= lv[j + 1] and lv[j] <= lv[j + 2]):
                cur_l = lv[j]
                lows.append((j, lv[j]))
                new_low = True
        if new_low:
            earlier_highs = [x for x in highs if x[0] < j]
            if earlier_highs:
                hc, hp = earlier_highs[-1]
                depth = (hp - lv[j]) / hp if hp != 0 else 0.0
                if depth > 0:
                    leg = {"start": hp, "start_centre": hc,
                           "extreme": lv[j], "depth": depth,
                           "vol": leg_vol(hc, j)}
                    if pullbacks and pullbacks[-1]["start_centre"] == hc:
                        pullbacks[-1] = leg  # same high, deeper low
                    else:
                        pullbacks.append(leg)
                    cur_vl, cur_ph = _chain_state(pullbacks, True)
        if new_high:
            earlier_lows = [x for x in lows if x[0] < j]
            if earlier_lows:
                lc, lp = earlier_lows[-1]
                depth = (hv[j] - lp) / lp if lp != 0 else 0.0
                if depth > 0:
                    leg = {"start": lp, "start_centre": lc,
                           "extreme": hv[j], "depth": depth,
                           "vol": leg_vol(lc, j)}
                    if rallies and rallies[-1]["start_centre"] == lc:
                        rallies[-1] = leg  # same low, higher high
                    else:
                        rallies.append(leg)
                    cur_vs, cur_pl = _chain_state(rallies, False)
        sh[i] = cur_h
        sl[i] = cur_l
        pivot_high[i] = cur_ph
        pivot_low[i] = cur_pl
        valid_long[i] = cur_vl
        valid_short[i] = cur_vs
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["sma50"] = B.sma(df["c"], 50)
    df["sma200"] = B.sma(df["c"], 200)
    df["pivot_high"] = pivot_high
    df["pivot_low"] = pivot_low
    df["vcp_valid"] = valid_long
    df["vcp_valid_short"] = valid_short
    df["vol_ma50"] = B.sma(df["v"], vol_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    return df
