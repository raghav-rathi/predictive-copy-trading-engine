"""ICT Balanced Price Range (BPR) indicators.

A fair value gap (FVG) is confirmed at bar i from bars i-2 and i:
bullish FVG iff low[i] > high[i-2], gap [high[i-2], low[i]];
bearish FVG iff high[i] < low[i-2], gap [low[i], high[i-2]].
A Balanced Price Range forms when a bullish and a bearish FVG
overlap in price AND the second forms within 60 bars of the first;
direction = direction of the LATER gap; zone = the overlap
[max of the two gap bottoms, min of the two gap tops]. Only the
most recent BPR per side is active.

Entry is a return into the zone: after a BPR forms, price must
first trade beyond it (bullish: a close above the zone top;
bearish: a close below the zone bottom), then the first close
inside the zone enters. A zone expires after 100 bars from
formation, or once price closes through it (close below a bullish
zone's bottom / above a bearish zone's top invalidates it). Each
zone enters once.

This is distinct from fvg_mitigation (a single FVG): the BPR is
the OVERLAP of two opposite gaps, and the entry requires the
return into that overlap after trading beyond it.

Columns:
    bull_bpr_bottom / bull_bpr_top -- active bullish BPR zone,
        NaN when none is active
    bear_bpr_bottom / bear_bpr_top -- active bearish BPR zone
    bpr_side -- +1 a bullish BPR is active, -1 a bearish BPR is
        active, 0 none (both active reports the bullish one)
    long_trigger / short_trigger -- True only on the entry bar
    atr -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
The FVG is recorded at its confirmation bar (i), never earlier.
"""

import numpy as np
import pandas as pd

from strategies import base as B

FVG_MAX_GAP_BARS = 60   # second FVG must form within 60 bars of the first
BPR_EXPIRY_BARS = 100   # zone expires 100 bars after formation

INDICATOR_COLS = ["bull_bpr_bottom", "bull_bpr_top",
                  "bear_bpr_bottom", "bear_bpr_top", "bpr_side", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)

    bull_bot = np.full(n, np.nan)
    bull_top = np.full(n, np.nan)
    bear_bot = np.full(n, np.nan)
    bear_top = np.full(n, np.nan)
    bpr_side = np.zeros(n, dtype=int)
    long_trig = np.zeros(n, dtype=bool)
    short_trig = np.zeros(n, dtype=bool)

    # Most recent FVG per direction: (bottom, top, formation bar).
    last_bull_fvg = None
    last_bear_fvg = None
    # Active BPR per side: dict(bottom, top, formed_idx, seen_away,
    # entered) or None.
    bull_bpr = None
    bear_bpr = None

    for i in range(n):
        # ---- FVG confirmed at bar i (bars i-2 and i) ----
        if i >= 2:
            if l[i] > h[i - 2]:
                gap = (float(h[i - 2]), float(l[i]))
                if (last_bear_fvg is not None
                        and i - last_bear_fvg[2] <= FVG_MAX_GAP_BARS):
                    bot = max(gap[0], last_bear_fvg[0])
                    top = min(gap[1], last_bear_fvg[1])
                    if bot < top:
                        bull_bpr = {"bottom": bot, "top": top,
                                    "formed_idx": i, "seen_away": False,
                                    "entered": False}
                last_bull_fvg = (gap[0], gap[1], i)
            elif h[i] < l[i - 2]:
                gap = (float(l[i]), float(h[i - 2]))
                if (last_bull_fvg is not None
                        and i - last_bull_fvg[2] <= FVG_MAX_GAP_BARS):
                    bot = max(gap[0], last_bull_fvg[0])
                    top = min(gap[1], last_bull_fvg[1])
                    if bot < top:
                        bear_bpr = {"bottom": bot, "top": top,
                                    "formed_idx": i, "seen_away": False,
                                    "entered": False}
                last_bear_fvg = (gap[0], gap[1], i)

        # ---- expiry (checked before publishing) ----
        if bull_bpr is not None and i - bull_bpr["formed_idx"] > BPR_EXPIRY_BARS:
            bull_bpr = None
        if bear_bpr is not None and i - bear_bpr["formed_idx"] > BPR_EXPIRY_BARS:
            bear_bpr = None

        # ---- entry / invalidation on this bar ----
        # The zone is published for this bar even on its
        # invalidation bar, so the signal layer sees the exit close.
        clear_bull_after = False
        clear_bear_after = False
        if bull_bpr is not None:
            if c[i] > bull_bpr["top"]:
                bull_bpr["seen_away"] = True
            elif c[i] < bull_bpr["bottom"]:
                clear_bull_after = True
            elif (bull_bpr["seen_away"] and not bull_bpr["entered"]
                    and bull_bpr["bottom"] <= c[i] <= bull_bpr["top"]):
                long_trig[i] = True
                bull_bpr["entered"] = True
        if bear_bpr is not None:
            if c[i] < bear_bpr["bottom"]:
                bear_bpr["seen_away"] = True
            elif c[i] > bear_bpr["top"]:
                clear_bear_after = True
            elif (bear_bpr["seen_away"] and not bear_bpr["entered"]
                    and bear_bpr["bottom"] <= c[i] <= bear_bpr["top"]):
                short_trig[i] = True
                bear_bpr["entered"] = True

        # ---- record this bar ----
        if bull_bpr is not None:
            bull_bot[i] = bull_bpr["bottom"]
            bull_top[i] = bull_bpr["top"]
        if bear_bpr is not None:
            bear_bot[i] = bear_bpr["bottom"]
            bear_top[i] = bear_bpr["top"]
        if bull_bpr is not None and bear_bpr is not None:
            bpr_side[i] = 1
        elif bull_bpr is not None:
            bpr_side[i] = 1
        elif bear_bpr is not None:
            bpr_side[i] = -1
        else:
            bpr_side[i] = 0
        if clear_bull_after:
            bull_bpr = None
        if clear_bear_after:
            bear_bpr = None

    df["bull_bpr_bottom"] = bull_bot
    df["bull_bpr_top"] = bull_top
    df["bear_bpr_bottom"] = bear_bot
    df["bear_bpr_top"] = bear_top
    df["bpr_side"] = bpr_side
    df["long_trigger"] = long_trig
    df["short_trigger"] = short_trig
    return df
