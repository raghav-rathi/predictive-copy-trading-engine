"""MACD Histogram Divergence indicators.

MACD(12, 26, 9) via strategies.base.ema:
    macd   = EMA(12) - EMA(26) of close
    signal = EMA(9) of macd
    hist   = macd - signal

Swing pivots (confirmed pivots only -- causal). Bar i is a swing
low if l[i] is the minimum of l[i-2..i+2] (and strictly below
l[i-1], which breaks ties toward the first occurrence); a swing
high is the mirror on h. The pivot is CONFIRMED at bar i+2, and
the divergence is evaluated at that confirmation bar, using data
through the confirmation bar only -- no lookahead.

Bullish divergence: a confirmed swing low whose low is LOWER than
the previous confirmed swing low within the last 60 bars, while
hist at that low is HIGHER than hist at the previous swing low,
AND hist turns up (hist[j] > hist[j-1]) on the confirmation bar j.
Bearish divergence is the mirror (swing highs, hist lower, hist
turns down on the confirmation bar).

Columns:
    macd_line / macd_signal / macd_hist -- MACD(12, 26, 9)
    pivot_low_conf / pivot_high_conf -- True on a confirmation bar
    pivot_low_price / pivot_low_hist -- price and hist at the
        confirmed swing low (NaN elsewhere); pivot_high_* mirror
    bull_div / bear_div -- True on a divergence confirmation bar
    atr -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9
PIVOT_N = 2
DIV_LOOKBACK = 60
ATR_N = 14


def add_indicators(df: pd.DataFrame, fast: int = FAST, slow: int = SLOW,
                   signal: int = SIGNAL, pivot_n: int = PIVOT_N,
                   div_lookback: int = DIV_LOOKBACK,
                   atr_n: int = ATR_N) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    m = B.macd(c, fast, slow, signal)
    df["macd_line"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], c, atr_n)

    l = df["l"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    hist = df["macd_hist"].to_numpy(dtype=float)
    n = len(df)

    pivot_low_conf = np.zeros(n, dtype=bool)
    pivot_high_conf = np.zeros(n, dtype=bool)
    bull_div = np.zeros(n, dtype=bool)
    bear_div = np.zeros(n, dtype=bool)
    pl_price = np.full(n, np.nan)
    pl_hist = np.full(n, np.nan)
    ph_price = np.full(n, np.nan)
    ph_hist = np.full(n, np.nan)

    lows: list[tuple[int, float, float]] = []   # (pivot bar, low, hist)
    highs: list[tuple[int, float, float]] = []  # (pivot bar, high, hist)

    for i in range(pivot_n, n - pivot_n):
        j = i + pivot_n  # confirmation bar
        # --- swing low at i, confirmed at j ---
        if (not np.isnan(l[i]) and l[i] == np.min(l[i - pivot_n:i + pivot_n + 1])
                and l[i] < l[i - 1]):
            pivot_low_conf[j] = True
            pl_price[j] = l[i]
            pl_hist[j] = hist[i]
            prev = [p for p in lows if i - p[0] <= div_lookback]
            if prev:
                pb, pp, ph = prev[-1]
                if (l[i] < pp and hist[i] > ph
                        and j >= 1 and hist[j] > hist[j - 1]):
                    bull_div[j] = True
            lows.append((i, float(l[i]), float(hist[i])))
        # --- swing high at i, confirmed at j ---
        if (not np.isnan(h[i]) and h[i] == np.max(h[i - pivot_n:i + pivot_n + 1])
                and h[i] > h[i - 1]):
            pivot_high_conf[j] = True
            ph_price[j] = h[i]
            ph_hist[j] = hist[i]
            prev = [p for p in highs if i - p[0] <= div_lookback]
            if prev:
                pb, pp, ph = prev[-1]
                if (h[i] > pp and hist[i] < ph
                        and j >= 1 and hist[j] < hist[j - 1]):
                    bear_div[j] = True
            highs.append((i, float(h[i]), float(hist[i])))

    df["pivot_low_conf"] = pivot_low_conf
    df["pivot_high_conf"] = pivot_high_conf
    df["pivot_low_price"] = pl_price
    df["pivot_low_hist"] = pl_hist
    df["pivot_high_price"] = ph_price
    df["pivot_high_hist"] = ph_hist
    df["bull_div"] = bull_div
    df["bear_div"] = bear_div
    return df
