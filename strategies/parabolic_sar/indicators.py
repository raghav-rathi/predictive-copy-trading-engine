"""Wilder Parabolic SAR indicators (J. Welles Wilder Jr., *New Concepts in
Technical Trading Systems*, 1978).

Classic SAR loop, vectorized where possible but a numpy loop for the SAR
state (5000 bars is fast):
  - Start: trend guess from the first bar's direction; AF starts at
    AF_START (0.02), EP = first extreme point.
  - Each new extreme point: AF += AF_STEP, capped at AF_MAX.
  - Update: sar[i] = sar[i-1] + AF*(EP - sar[i-1]).
  - Clamp: long SAR may not exceed the prior two bars' lows;
    short SAR may not go below the prior two bars' highs.
  - Flip (computed on bar i using only data through i): long and
    low[i] < sar[i] (or the clamped SAR was penetrated) -> flip to short:
    sar_dir[i] = -1, AF reset to AF_START, EP = low[i],
    sar = prior EP (extreme of the old trend). Mirror for short->long.

No lookahead: every value at bar i uses only bars through i.
"""

import numpy as np
import pandas as pd

AF_START = 0.02
AF_STEP = 0.02
AF_MAX = 0.20


def parabolic_sar(h: np.ndarray, l: np.ndarray, c: np.ndarray,
                  af_start: float = AF_START, af_step: float = AF_STEP,
                  af_max: float = AF_MAX):
    """Compute Wilder SAR. Returns (sar, sar_dir, af) numpy arrays.

    sar_dir is +1 (long) / -1 (short). Early bars before a valid flip
    state settle to whatever the loop initialized (never NaN).
    """
    n = len(c)
    sar = np.full(n, np.nan)
    d = np.full(n, 0, dtype=np.int8)
    af = np.full(n, np.nan)

    if n < 2:
        return sar, d, af

    # Initial trend guess: up if the first close is above the first open
    # proxy (use first two closes here since we get h/l/c).
    long = c[1] >= c[0]
    if long:
        cur_sar = l[0]
        ep = h[0]
    else:
        cur_sar = h[0]
        ep = l[0]
    a = af_start
    d[0] = 1 if long else -1
    sar[0] = cur_sar
    af[0] = a

    for i in range(1, n):
        prev_dir = d[i - 1]
        prev_sar = sar[i - 1]

        if prev_dir == 1:
            # Update EP/AF on new high
            if h[i] > ep:
                ep = h[i]
                a = min(a + af_step, af_max)
            raw = prev_sar + a * (ep - prev_sar)
            # Clamp: long SAR may not exceed the prior two bars' lows
            lo = l[i - 1] if i == 1 else min(l[i - 1], l[i - 2])
            raw = min(raw, lo)
            if l[i] < raw:
                # flip to short
                sar[i] = ep            # prior extreme becomes the SAR
                d[i] = -1
                a = af_start
                ep = l[i]
            else:
                sar[i] = raw
                d[i] = 1
        else:
            if l[i] < ep:
                ep = l[i]
                a = min(a + af_step, af_max)
            raw = prev_sar + a * (ep - prev_sar)
            # Clamp: short SAR may not go below the prior two bars' highs
            hi = h[i - 1] if i == 1 else max(h[i - 1], h[i - 2])
            raw = max(raw, hi)
            if h[i] > raw:
                sar[i] = ep
                d[i] = 1
                a = af_start
                ep = h[i]
            else:
                sar[i] = raw
                d[i] = -1
        af[i] = a

    return sar, d, af


def add_indicators(df: pd.DataFrame, af_start: float = AF_START,
                   af_step: float = AF_STEP, af_max: float = AF_MAX) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    sar, d, af = parabolic_sar(h, l, c, af_start=af_start, af_step=af_step,
                               af_max=af_max)
    df["sar"] = sar
    df["sar_dir"] = d.astype(int)
    df["sar_af"] = af
    return df
