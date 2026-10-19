"""Laguerre RSI indicators (John Ehlers), per the source's formula.

Recurrence (numpy loop over closes, seed L* = first close):
    L0[i] = (1-g)*c[i] + g*L0[i-1]
    L1[i] = -g*L0[i] + L0[i-1] + g*L1[i-1]
    L2[i] = -g*L1[i] + L1[i-1] + g*L2[i-1]
    L3[i] = -g*L2[i] + L2[i-1] + g*L3[i-1]
    CU    = (L0 + L1 + L2 + L3) / 4

Per-bar oscillator (this is the source's literal spec, verified
2026-10-19 -- NOT a running sum):
    diff = CU - CU_prev          (diff[0] = 0)
    UP   = max(diff, 0)          (per bar, not cumulative)
    DN   = -min(diff, 0)         (per bar, not cumulative)
    lrsi = UP / (UP + DN);  UP+DN == 0 -> previous lrsi (seed 0.5)

A running-sum reading of the source (cumup/(cumup+cumdn)) was tried
first: the ratio converges to the long-run up-move fraction and stops
moving, producing 1 trade in 7 months. The source text is unambiguous
("If CU >= CU_old: UP = CU - CU_old, DN = 0 ... LRSI = UP/(UP+DN)"),
so the per-bar form ships. Consequence: lrsi only takes values
{0, 0.5, 1} -- it is the sign of the Laguerre-filtered momentum, and
the 0.2/0.8/0.5 signal levels become direction-flip triggers.

No lookahead: every value on bar i uses bars through i only.

Source: https://doc.stocksharp.com/en/topics/api/indicators/list_of_indicators/laguerre_rsi
"""

import numpy as np
import pandas as pd

from strategies import base as B

GAMMA = 0.5
SEED_LRSI = 0.5


def _laguerre_levels(prices: np.ndarray, gamma: float):
    """Return (L0, L1, L2, L3) as numpy arrays."""
    n = len(prices)
    L0 = np.empty(n)
    L1 = np.empty(n)
    L2 = np.empty(n)
    L3 = np.empty(n)
    L0[0] = L1[0] = L2[0] = L3[0] = prices[0]
    g = gamma
    for i in range(1, n):
        L0[i] = (1.0 - g) * prices[i] + g * L0[i - 1]
        L1[i] = -g * L0[i] + L0[i - 1] + g * L1[i - 1]
        L2[i] = -g * L1[i] + L1[i - 1] + g * L2[i - 1]
        L3[i] = -g * L2[i] + L2[i - 1] + g * L3[i - 1]
    return L0, L1, L2, L3


def add_indicators(df: pd.DataFrame, gamma: float = GAMMA) -> pd.DataFrame:
    df = df.copy()
    c = df["c"].to_numpy(dtype=float)
    n = len(c)
    L0, L1, L2, L3 = _laguerre_levels(c, gamma)
    df["lag_L0"] = L0
    df["lag_L1"] = L1
    df["lag_L2"] = L2
    df["lag_L3"] = L3
    cu = (L0 + L1 + L2 + L3) / 4.0
    df["lag_CU"] = cu
    diff = np.empty(n)
    diff[0] = 0.0
    diff[1:] = cu[1:] - cu[:-1]
    df["lag_diff"] = diff
    up = np.maximum(diff, 0.0)
    dn = np.maximum(-diff, 0.0)
    denom = up + dn
    ratio = np.full(n, np.nan)
    nz = denom > 0.0
    ratio[nz] = up[nz] / denom[nz]
    lrsi = pd.Series(ratio).ffill().fillna(SEED_LRSI).to_numpy()
    df["lrsi"] = lrsi
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
