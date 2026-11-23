"""MACD + RSI divergence indicators (causal, no lookahead).

NOTE ON THE NAME: the slug is ``macd_rsi_divergence`` but this
implementation is MACD-only for both sides, per the build spec.
RSI divergence was NOT implemented — RSI(14) is computed and
exposed as a column for inspection, but no signal reads it. See
README.md / CALIBRATION.md.

Confirmed pivots
----------------
A price low is a *confirmed* pivot at bar i when the low of bar
i-2 is the strict lowest low of the +/-2-bar window around it,
i.e. ``l[i-2] < min(l[i-4:i-2], l[i-1:i+1])``. The pivot bar is
i-2; bar i is the confirmation bar, and the signal is only
available at bar i (two bars of confirmation). High pivots are
the mirror with the strict highest high. Strict inequality avoids
duplicate pivots on flat equal lows/highs. All comparisons use
data through bar i only — the pivot test at bar i never looks
past bar i.

Divergence (regular only, MACD histogram)
-----------------------------------------
Bullish: a confirmed pivot low is LOWER than the previous
confirmed pivot low, while the MACD histogram at the new pivot
is HIGHER than at the previous pivot low. Bearish is the mirror
(higher high, lower histogram). The histogram is
``base.macd`` (12, 26, 9) — the classic Appel MACD with the
Aspray histogram. The divergence flag is set on the
confirmation bar (pivot + 2); the entry additionally requires
the histogram to be rising on that bar (checked in signals.py),
so ``bullish_divergence`` alone is the pivot comparison, not
the full entry condition.

Seeding: MACD EMAs need 26 bars before the slow EMA is defined;
``macd`` / ``macd_signal`` / ``macd_hist`` are NaN before that
and are deterministically seeded to 0.0 (documented here — the
first bars have no momentum reading, and WARMUP = 60 bars
covers the seeding window). Pivot/divergence booleans are False
where undefined, so no signal column ever carries NaN. RSI(14)
is seeded by ``base.rsi`` itself (100 where only gains, 0 where
only losses) and is not used by any signal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_HALF = 2


def _confirmed_pivots(l: np.ndarray, h: np.ndarray):
    """Return (pivot_low_confirmed, pivot_high_confirmed) boolean
    arrays, True on the confirmation bar (pivot bar + 2)."""
    n = len(l)
    pl = np.zeros(n, dtype=bool)
    ph = np.zeros(n, dtype=bool)
    for i in range(2 * PIVOT_HALF, n):
        p = i - PIVOT_HALF
        window_l = np.concatenate([l[i - 4:i - 2], l[i - 1:i + 1]])
        window_h = np.concatenate([h[i - 4:i - 2], h[i - 1:i + 1]])
        if l[p] < window_l.min():
            pl[i] = True
        if h[p] > window_h.max():
            ph[i] = True
    return pl, ph


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    macd = B.macd(c)
    df["macd"] = macd["macd"].fillna(0.0)
    df["macd_signal"] = macd["macd_signal"].fillna(0.0)
    df["macd_hist"] = macd["macd_hist"].fillna(0.0)
    df["rsi14"] = B.rsi(c, 14)

    l_v = l.to_numpy(dtype=float)
    h_v = h.to_numpy(dtype=float)
    hist_v = df["macd_hist"].to_numpy(dtype=float)
    n = len(df)

    pl, ph = _confirmed_pivots(l_v, h_v)
    df["pivot_low_confirmed"] = pl
    df["pivot_high_confirmed"] = ph

    # Pivot price / histogram at the pivot bar, placed on the
    # confirmation bar; NaN where no pivot is confirmed.
    pl_price = np.full(n, np.nan)
    pl_hist = np.full(n, np.nan)
    ph_price = np.full(n, np.nan)
    ph_hist = np.full(n, np.nan)
    for i in range(n):
        if pl[i]:
            pl_price[i] = l_v[i - PIVOT_HALF]
            pl_hist[i] = hist_v[i - PIVOT_HALF]
        if ph[i]:
            ph_price[i] = h_v[i - PIVOT_HALF]
            ph_hist[i] = hist_v[i - PIVOT_HALF]
    df["pivot_low_price"] = pl_price
    df["pivot_low_hist"] = pl_hist
    df["pivot_high_price"] = ph_price
    df["pivot_high_hist"] = ph_hist

    # Regular divergence vs the previous confirmed pivot, flagged
    # on the confirmation bar.
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)
    prev_low_price = prev_low_hist = None
    prev_high_price = prev_high_hist = None
    for i in range(n):
        if pl[i]:
            if prev_low_price is not None:
                if pl_price[i] < prev_low_price and pl_hist[i] > prev_low_hist:
                    bull[i] = True
            prev_low_price, prev_low_hist = pl_price[i], pl_hist[i]
        if ph[i]:
            if prev_high_price is not None:
                if ph_price[i] > prev_high_price and ph_hist[i] < prev_high_hist:
                    bear[i] = True
            prev_high_price, prev_high_hist = ph_price[i], ph_hist[i]
    df["bullish_divergence"] = bull
    df["bearish_divergence"] = bear
    return df
