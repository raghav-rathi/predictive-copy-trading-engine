"""Ichimoku cloud + Stochastic signals.

LONG when all three hold on bar i:
- close > cloud top (max of Senkou A/B — price above the cloud),
- Tenkan > Kijun (short-term momentum above baseline),
- %K crosses above %D while %K < 30 (Stochastic turning up from
  oversold).

SHORT is the mirror: close < cloud bottom, Tenkan < Kijun, %K
crosses below %D while %K > 70.

Exits (state machine, one pass):
- Long: %K crosses below %D (opposite cross), OR close falls
  back to/below the cloud top (close <= cloud top — back inside
  or through the cloud).
- Short: %K crosses above %D, OR close rises back to/above the
  cloud bottom (close >= cloud_bottom).
- An exit on a bar that also carries the opposite entry
  condition flips the position (exit + entry on the same bar).

Entries are transition-only: a signal fires only when flat (or
on a flip bar). While a position is held, repeated qualifying
bars do NOT re-enter. The %K < 30 / > 70 gate is read on the
cross bar itself. All conditions read bar-i values at bar i;
signal columns are boolean, no NaN, no lookahead. Execution is
at bar i+1's open per the house convention.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(dtype=float)
    tenkan = df["tenkan"].to_numpy(dtype=float)
    kijun = df["kijun"].to_numpy(dtype=float)
    top = df["cloud_top"].to_numpy(dtype=float)
    bottom = df["cloud_bottom"].to_numpy(dtype=float)
    k = df["stoch_k"].to_numpy(dtype=float)
    d = df["stoch_d"].to_numpy(dtype=float)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short" / None
    for i in range(n):
        cross_up = i > 0 and k[i] > d[i] and k[i - 1] <= d[i - 1]
        cross_dn = i > 0 and k[i] < d[i] and k[i - 1] >= d[i - 1]
        if pos == "long":
            if cross_dn or c[i] <= top[i]:
                lx[i] = True
                pos = None
        elif pos == "short":
            if cross_up or c[i] >= bottom[i]:
                sx[i] = True
                pos = None
        if pos is None:
            if c[i] > top[i] and tenkan[i] > kijun[i] and cross_up and k[i] < 30:
                le[i] = True
                pos = "long"
            elif c[i] < bottom[i] and tenkan[i] < kijun[i] and cross_dn and k[i] > 70:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
