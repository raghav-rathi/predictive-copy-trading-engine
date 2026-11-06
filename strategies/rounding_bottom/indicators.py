"""Rounding Bottom indicators: rolling 60-bar saucer detection + ATR(14).

Per window ending at bar i (60 bars, i-59..i):
- trough = window minimum close, required to sit in the middle third
  (window positions 20..39);
- left rim = max close in the first 15 bars, right rim = max close in the
  last 15 bars; rims must agree within 2%;
- trough at least 3x ATR(14) below the lower rim;
- U-shape: 10-bar SMA slope negative over the first half of the window
  and positive over the second half.
The rounding-top mirror inverts trough/peak and the slope signs.
Detected necklines are forward-filled so the breakout can be tested on
later bars; ``rb_bars_since`` / ``rt_bars_since`` count bars since the
last detection (NaN before any detection).
"""

import numpy as np
import pandas as pd

from strategies import base as B

INDICATOR_COLS = [
    "atr14",
    "sma10",
    "vol_sma20",
    "neckline_bottom",
    "neckline_top",
    "rb_pattern",
    "rt_pattern",
    "rb_bars_since",
    "rt_bars_since",
]

WINDOW = 60


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    v = df["v"].to_numpy(dtype=float)
    n = len(df)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    df["sma10"] = B.sma(df["c"], 10)
    df["vol_sma20"] = B.sma(df["v"], 20)
    atr = df["atr14"].to_numpy(dtype=float)
    sma10 = df["sma10"].to_numpy(dtype=float)

    rb_neck = np.full(n, np.nan)
    rt_neck = np.full(n, np.nan)
    rb_pat = np.zeros(n, dtype=float)
    rt_pat = np.zeros(n, dtype=float)
    rb_since = np.full(n, np.nan)
    rt_since = np.full(n, np.nan)
    last_rb = None
    last_rt = None

    for i in range(WINDOW - 1, n):
        w = c[i - WINDOW + 1 : i + 1]
        mid = w[20:40]
        trough = mid.min()
        # Trough must be in the middle third (it is, by construction of mid).
        left_rim = w[:15].max()
        right_rim = w[45:].max()
        a = atr[i]
        if np.isfinite(a) and a > 0:
            rims_close = abs(left_rim - right_rim) / ((left_rim + right_rim) / 2) <= 0.02
            deep = trough <= min(left_rim, right_rim) - 3.0 * a
            s0, s30, s59 = sma10[i - 59], sma10[i - 30], sma10[i]
            if np.isfinite(s0) and np.isfinite(s30) and np.isfinite(s59):
                u_shape = (s30 - s0 < 0) and (s59 - s30 > 0)
                if rims_close and deep and u_shape:
                    rb_pat[i] = 1.0
                    rb_neck[i] = left_rim
                    last_rb = i
        # Rounding top mirror.
        peak = mid.max()
        left_rim_lo = w[:15].min()
        right_rim_lo = w[45:].min()
        if np.isfinite(a) and a > 0:
            rims_close = abs(left_rim_lo - right_rim_lo) / ((left_rim_lo + right_rim_lo) / 2) <= 0.02
            high_enough = peak >= max(left_rim_lo, right_rim_lo) + 3.0 * a
            s0, s30, s59 = sma10[i - 59], sma10[i - 30], sma10[i]
            if np.isfinite(s0) and np.isfinite(s30) and np.isfinite(s59):
                n_shape = (s30 - s0 > 0) and (s59 - s30 < 0)
                if rims_close and high_enough and n_shape:
                    rt_pat[i] = 1.0
                    rt_neck[i] = left_rim_lo
                    last_rt = i
        if last_rb is not None:
            rb_since[i] = i - last_rb
        if last_rt is not None:
            rt_since[i] = i - last_rt

    df["neckline_bottom"] = pd.Series(rb_neck, index=df.index).ffill()
    df["neckline_top"] = pd.Series(rt_neck, index=df.index).ffill()
    df["rb_pattern"] = rb_pat
    df["rt_pattern"] = rt_pat
    df["rb_bars_since"] = rb_since
    df["rt_bars_since"] = rt_since
    return df
