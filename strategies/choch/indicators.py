"""Change of Character (ChoCh) indicators.

Same causal 5-bar pivots as sfp (centre+2 confirmation, recorded at
the confirmation bar; see sfp/indicators.py for the rule). A state
machine loop over bars tracks the pivot sequence:

- uptrend (trend = 1): the last two confirmed swing highs are
  rising AND the last two confirmed swing lows are rising (HH/HL).
- downtrend (trend = -1): the last two swing highs are falling AND
  the last two swing lows are falling (LL/LH).
- otherwise the previous trend is retained (0 until the first
  HH/HL or LL/LH pair forms); structure does not flip on a single
  mixed pivot.
- protected_low: in an uptrend, the swing low that produced the
  most recent swing high (the latest swing low with centre before
  that high's centre). protected_high: the mirror in a downtrend
  (the latest swing high with centre before the most recent swing
  low's centre). Both forward-fill; NaN until first defined.

Columns:
    swing_high, swing_low -- last confirmed pivot levels
    protected_low, protected_high -- structure levels above
    trend              -- 1 up / -1 down / 0 none
    atr                -- Wilder ATR(14)
    body_atr           -- |close - open| / ATR(14) (displacement)

No lookahead: every value on bar i uses data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ATR_N = 14

INDICATOR_COLS = ["swing_high", "swing_low", "protected_low",
                  "protected_high", "trend", "atr", "body_atr"]


def add_indicators(df: pd.DataFrame, atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    hv = df["h"].to_numpy(dtype=float)
    lv = df["l"].to_numpy(dtype=float)
    n = len(hv)
    sh = np.full(n, np.nan)
    sl = np.full(n, np.nan)
    prot_low = np.full(n, np.nan)
    prot_high = np.full(n, np.nan)
    trend = np.zeros(n, dtype=float)
    highs: list[tuple[int, float]] = []  # (centre, price), centre order
    lows: list[tuple[int, float]] = []
    cur_h = np.nan
    cur_l = np.nan
    cur_trend = 0
    cur_pl = np.nan
    cur_ph = np.nan
    for i in range(n):
        j = i - 2
        if j >= 2:
            if (hv[j] > hv[j - 1] and hv[j] > hv[j - 2]
                    and hv[j] >= hv[j + 1] and hv[j] >= hv[j + 2]):
                cur_h = hv[j]
                highs.append((j, hv[j]))
            if (lv[j] < lv[j - 1] and lv[j] < lv[j - 2]
                    and lv[j] <= lv[j + 1] and lv[j] <= lv[j + 2]):
                cur_l = lv[j]
                lows.append((j, lv[j]))
        if len(highs) >= 2 and len(lows) >= 2:
            hh = highs[-1][1] > highs[-2][1]
            hl = lows[-1][1] > lows[-2][1]
            ll = lows[-1][1] < lows[-2][1]
            lh = highs[-1][1] < highs[-2][1]
            if hh and hl:
                cur_trend = 1
            elif ll and lh:
                cur_trend = -1
            # mixed structure: retain the previous trend
        if cur_trend == 1 and highs:
            last_h_centre = highs[-1][0]
            earlier = [p for (c, p) in lows if c < last_h_centre]
            if earlier:
                cur_pl = earlier[-1]
        elif cur_trend == -1 and lows:
            last_l_centre = lows[-1][0]
            earlier = [p for (c, p) in highs if c < last_l_centre]
            if earlier:
                cur_ph = earlier[-1]
        sh[i] = cur_h
        sl[i] = cur_l
        prot_low[i] = cur_pl
        prot_high[i] = cur_ph
        trend[i] = cur_trend
    df["swing_high"] = sh
    df["swing_low"] = sl
    df["protected_low"] = prot_low
    df["protected_high"] = prot_high
    df["trend"] = trend
    df["atr"] = B.atr(df["h"], df["l"], df["c"], atr_n)
    df["body_atr"] = (df["c"] - df["o"]).abs() / df["atr"]
    return df
