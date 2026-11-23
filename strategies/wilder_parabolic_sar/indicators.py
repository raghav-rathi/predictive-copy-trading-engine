"""Wilder Parabolic SAR indicators (implemented from scratch).

Classic Wilder PSAR (J. Welles Wilder, *New Concepts in Technical
Trading Systems*, 1978), AF step 0.02, max AF 0.20.

State machine, bar by bar:
- LONG: SAR[i] = SAR[i-1] + AF * (EP - SAR[i-1]), where EP is the
  highest high since the trend began. SAR is clamped so it never
  exceeds the lowest low of the prior two bars (Wilder's rule:
  the stop can never be above the two most recent lows in an
  uptrend). If low[i] < SAR[i] the trend flips to SHORT.
- SHORT: mirror image (SAR below price, clamped to the highest
  high of the prior two bars; flip when high[i] > SAR[i]).
- On a flip the new SAR is the old EP (the extreme point of the
  trend just ended), the new EP is the current bar's extreme
  (low on a flip to short, high on a flip to long), and AF
  resets to the 0.02 step.
- While the trend continues and price makes a new extreme,
  EP updates and AF grows by 0.02 per new extreme, capped at
  0.20.

Seeding (documented choice): bar 0 starts LONG with
SAR = low[0], EP = high[0], AF = 0.02. There is no prior trend
to infer, so the seed is arbitrary; the signal layer treats
bar 0 as *no entry* (see signals.py) and only enters on a
subsequent flip, so the seed cannot manufacture a trade. The
seed washes out within a few bars on real data because the
first flip re-anchors SAR to a genuine extreme point.

Columns:
    psar      -- the SAR stop level (no NaN; seeded from bar 0)
    psar_dir  -- +1 long trend, -1 short trend (no NaN)
    psar_ep   -- extreme point of the current trend
    psar_af   -- acceleration factor in force on that bar
    atr       -- ATR(14) for the risk layer

No lookahead: every value on bar i uses only bars 0..i.
"""

import numpy as np
import pandas as pd

from strategies import base as B

AF_STEP = 0.02
AF_MAX = 0.20


def parabolic_sar(h, l, step: float = AF_STEP, max_af: float = AF_MAX):
    """Wilder Parabolic SAR. Returns (sar, direction, ep, af) arrays.

    direction is +1 while the trend is long, -1 while short.
    """
    h_v = np.asarray(h, dtype=float)
    l_v = np.asarray(l, dtype=float)
    n = len(h_v)
    sar = np.full(n, np.nan)
    ep = np.full(n, np.nan)
    af = np.full(n, step)
    direction = np.ones(n, dtype=int)
    if n == 0:
        return sar, direction, ep, af

    # Seed LONG from bar 0 (see module docstring).
    direction[0] = 1
    sar[0] = l_v[0]
    ep[0] = h_v[0]
    af[0] = step

    for i in range(1, n):
        prev_dir = direction[i - 1]
        prev_sar = sar[i - 1]
        prev_ep = ep[i - 1]
        prev_af = af[i - 1]
        if prev_dir == 1:
            s = prev_sar + prev_af * (prev_ep - prev_sar)
            # Clamp: SAR may not exceed the lowest low of the prior
            # two bars (one prior bar on i == 1).
            floor = l_v[i - 1] if i == 1 else min(l_v[i - 1], l_v[i - 2])
            s = min(s, floor)
            if l_v[i] < s:
                # Flip to SHORT: SAR restarts at the old extreme.
                direction[i] = -1
                sar[i] = prev_ep
                ep[i] = l_v[i]
                af[i] = step
            else:
                direction[i] = 1
                sar[i] = s
                if h_v[i] > prev_ep:
                    ep[i] = h_v[i]
                    af[i] = min(prev_af + step, max_af)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af
        else:
            s = prev_sar + prev_af * (prev_ep - prev_sar)
            # Clamp: SAR may not go below the highest high of the
            # prior two bars.
            ceil = h_v[i - 1] if i == 1 else max(h_v[i - 1], h_v[i - 2])
            s = max(s, ceil)
            if h_v[i] > s:
                # Flip to LONG.
                direction[i] = 1
                sar[i] = prev_ep
                ep[i] = h_v[i]
                af[i] = step
            else:
                direction[i] = -1
                sar[i] = s
                if l_v[i] < prev_ep:
                    ep[i] = l_v[i]
                    af[i] = min(prev_af + step, max_af)
                else:
                    ep[i] = prev_ep
                    af[i] = prev_af
    return sar, direction, ep, af


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sar, direction, ep, af = parabolic_sar(df["h"], df["l"])
    df["psar"] = sar
    df["psar_dir"] = direction
    df["psar_ep"] = ep
    df["psar_af"] = af
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
