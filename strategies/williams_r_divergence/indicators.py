"""Williams %R divergence indicators (causal, no lookahead).

Larry Williams, Williams %R divergence: %R(14) =
-100 * (highest high(14) - close) / (highest high(14) -
lowest low(14)).

Confirmed pivots
----------------
The pivot machinery follows strategies/macd_rsi_divergence
exactly (±2-bar pivots). A price low is a *confirmed* pivot
at bar i when the low of bar i-2 is the strict lowest low of
the +/-2-bar window around it, i.e. ``l[i-2] < min(l[i-4:i-2],
l[i-1:i+1])``. The pivot bar is i-2; bar i is the
confirmation bar, and the signal is only available at bar i
(two bars of confirmation). High pivots are the mirror with
the strict highest high. Strict inequality avoids duplicate
pivots on flat equal lows/highs. All comparisons use data
through bar i only — the pivot test at bar i never looks past
bar i.

Divergence (regular only, Williams %R)
--------------------------------------
Bullish: a confirmed pivot low is LOWER than the previous
confirmed pivot low, while %R at the new pivot is HIGHER
than %R at the previous pivot low, AND %R < -80 at the new
pivot. Bearish is the mirror (higher high, lower %R, %R >
-20 at the pivot). The divergence flag is set on the
confirmation bar (pivot + 2); the entry fires on that bar
(checked in signals.py).

Columns:
    williams_r            -- %R(14); -50 where the 14-bar
                             range is 0 (flat bar: no range,
                             neutral reading)
    pivot_low_confirmed / pivot_high_confirmed -- True on the
                             confirmation bar
    pivot_low_price / pivot_high_price -- price at the pivot bar
    pivot_low_wr / pivot_high_wr -- %R at the pivot bar
    bullish_divergence / bearish_divergence -- flagged on the
                             confirmation bar
    atr14                 -- ATR(14), diagnostic

%R is NaN before 14 bars; WARMUP = 30 covers the spin-up.
Pivot/divergence booleans are False where undefined, so no
signal column ever carries NaN. No chikou or future bar is
used anywhere.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIVOT_HALF = 2
WR_N = 14


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


def add_indicators(
    df: pd.DataFrame,
    wr_n: int = WR_N,
    pivot_half: int = PIVOT_HALF,
) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    hh = h.rolling(wr_n, min_periods=wr_n).max()
    ll = l.rolling(wr_n, min_periods=wr_n).min()
    rng = hh - ll
    df["williams_r"] = (-100.0 * (hh - c) / rng).where(rng > 0, -50.0)
    df["atr14"] = B.atr(h, l, c, 14)

    l_v = l.to_numpy(dtype=float)
    h_v = h.to_numpy(dtype=float)
    wr_v = df["williams_r"].to_numpy(dtype=float)
    n = len(df)

    pl, ph = _confirmed_pivots(l_v, h_v)
    df["pivot_low_confirmed"] = pl
    df["pivot_high_confirmed"] = ph

    # Pivot price / %R at the pivot bar, placed on the
    # confirmation bar; NaN where no pivot is confirmed.
    pl_price = np.full(n, np.nan)
    pl_wr = np.full(n, np.nan)
    ph_price = np.full(n, np.nan)
    ph_wr = np.full(n, np.nan)
    for i in range(n):
        if pl[i]:
            pl_price[i] = l_v[i - pivot_half]
            pl_wr[i] = wr_v[i - pivot_half]
        if ph[i]:
            ph_price[i] = h_v[i - pivot_half]
            ph_wr[i] = wr_v[i - pivot_half]
    df["pivot_low_price"] = pl_price
    df["pivot_low_wr"] = pl_wr
    df["pivot_high_price"] = ph_price
    df["pivot_high_wr"] = ph_wr

    # Regular divergence vs the previous confirmed pivot, flagged
    # on the confirmation bar. Bullish additionally requires
    # %R < -80 at the new pivot; bearish requires %R > -20.
    bull = np.zeros(n, dtype=bool)
    bear = np.zeros(n, dtype=bool)
    prev_low_price = prev_low_wr = None
    prev_high_price = prev_high_wr = None
    for i in range(n):
        if pl[i]:
            if prev_low_price is not None:
                if (pl_price[i] < prev_low_price
                        and pl_wr[i] > prev_low_wr
                        and pl_wr[i] < -80.0):
                    bull[i] = True
            prev_low_price, prev_low_wr = pl_price[i], pl_wr[i]
        if ph[i]:
            if prev_high_price is not None:
                if (ph_price[i] > prev_high_price
                        and ph_wr[i] < prev_high_wr
                        and ph_wr[i] > -20.0):
                    bear[i] = True
            prev_high_price, prev_high_wr = ph_price[i], ph_wr[i]
    df["bullish_divergence"] = bull
    df["bearish_divergence"] = bear
    return df
