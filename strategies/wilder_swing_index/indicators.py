"""Welles Wilder's Swing Index and Accumulation Swing Index (ASI).

Per-bar Swing Index (Wilder, "New Concepts in Technical Trading Systems"):

    SI = 50 x [(C - Cy) + 0.5(C - O) + K(T - Cy)] / R

    Cy = previous close
    K  = 0.5 x (max(H, Cy) - min(L, Cy)) / (H - L); 0 if H == L
    T  = H if (H - Cy) > (Cy - L) else L
    R  = (H - Cy) - 0.5(L - Cy) + 0.25(Cy - O)   if (H - Cy) > (Cy - L)
       = (Cy - L) - 0.5(H - Cy) + 0.25(Cy - O)   if (Cy - L) > (H - Cy)
       = (H - L) + 0.25(Cy - O)                 otherwise

A limit-up day (O = Cy, C = H = Cy + limit) scores exactly +100, and a
limit-down day -100, which is Wilder's calibration. ASI = cumsum(SI).

No lookahead: every value on bar i uses bars through i only (SI needs the
previous close, so the first bar scores 0).
"""

import numpy as np
import pandas as pd

from strategies import base as B

BREAKOUT_WINDOW = 20


def swing_index(o: pd.Series, h: pd.Series, l: pd.Series, c: pd.Series) -> pd.Series:
    """Per-bar Wilder Swing Index as a pandas Series (index preserved)."""
    cy = c.shift(1)
    up_gap = h - cy      # H - Cy
    dn_gap = cy - l      # Cy - L
    hl = h - l
    # K: 0 when H == L (flat bar)
    k = (0.5 * (np.maximum(h, cy) - np.minimum(l, cy)) / hl.where(hl != 0)).fillna(0.0)
    t = np.where(up_gap > dn_gap, h, l)
    r_up = up_gap - 0.5 * (l - cy) + 0.25 * (cy - o)
    r_dn = dn_gap - 0.5 * (h - cy) + 0.25 * (cy - o)
    r_eq = hl + 0.25 * (cy - o)
    r = np.where(up_gap > dn_gap, r_up, np.where(dn_gap > up_gap, r_dn, r_eq))
    si = 50.0 * ((c - cy) + 0.5 * (c - o) + k * (t - cy)) / np.where(r == 0, np.nan, r)
    return si.fillna(0.0)


def add_indicators(df: pd.DataFrame, breakout_window: int = BREAKOUT_WINDOW) -> pd.DataFrame:
    df = df.copy()
    si = swing_index(df["o"], df["h"], df["l"], df["c"])
    df["swing_index"] = si
    asi = si.cumsum()
    df["asi"] = asi
    prior = asi.shift(1)
    df["asi_prior_high"] = prior.rolling(breakout_window, min_periods=breakout_window).max()
    df["asi_prior_low"] = prior.rolling(breakout_window, min_periods=breakout_window).min()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
