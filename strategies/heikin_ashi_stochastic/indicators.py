"""Heikin Ashi + Stochastic indicators (causal, no lookahead).

Heikin Ashi candles (Munehisa Homma; StockCharts ChartSchool):

    ha_close = (o + h + l + c) / 4
    ha_open  = (prev ha_open + prev ha_close) / 2, seeded ha_open[0] = o[0]
    ha_high  = max(h, ha_open, ha_close)
    ha_low   = min(l, ha_open, ha_close)

The recursion reads only the previous bar's HA values and the
current bar's OHLC, so every HA value on bar i uses data through
bar i only. Seeding note: the spec fixes ha_open[0] = o[0]
(StockCharts instead seeds the first HA open to (o+c)/2 and
starts the calculation before the first visible bar). The
difference washes out within a few bars — HA open converges to
the same recursion regardless of seed — and WARMUP = 60 bars
covers the seeding window many times over.

Trend filter: ha_ema50 = EMA(50) of ha_close (``base.ema``,
min_periods=50, so NaN before bar 49). The NaN region is
filled with ha_close itself, which makes ``ha_close >
ha_ema50`` False there (no trend read before the EMA exists)
instead of leaking NaNs into downstream comparisons.

Stochastic Oscillator (George Lane; StockCharts ChartSchool),
Fast %K with a 3-period %D — exactly the formulas in the
build spec:

    %K = 100 * (c - lowest low 14) / (highest high 14 - lowest low 14)
    %D = SMA(3) of %K

Note: this is the Fast %K (raw ratio) with %D as its 3-period
SMA — the "14,3" fast form. It is NOT the Slow/Full form
(14,3,3), where %K itself is first smoothed by 3 and %D is a
second 3-period average. The spec's explicit formulas define
the fast form, so that is what is implemented; see
CALIBRATION.md.

Edge cases: a zero 14-bar range (highest high == lowest low,
flat bars) makes the ratio 0/0; %K is set to 50.0 (neutral)
there. Before the 14-bar window fills, %K is NaN and is
filled with 50.0 for the same reason — no oversold/overbought
read exists yet, and WARMUP = 60 covers the region. %K and
%D are therefore always in [0, 100] with no NaN.

Columns:
    ha_open, ha_high, ha_low, ha_close -- Heikin Ashi candles
    ha_ema50                          -- EMA(50) of ha_close
    stoch_k, stoch_d                  -- Stochastic %K / %D
"""

import numpy as np
import pandas as pd

from strategies import base as B

STOCH_N = 14
STOCH_K_SMOOTH = 1  # raw %K (fast form); see module docstring
STOCH_D_N = 3
HA_EMA_N = 50


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    n = len(df)

    ha_close = (o + h + l + c) / 4.0
    ha_open = np.empty(n, dtype=float)
    if n:
        ha_open[0] = o[0]
        for i in range(1, n):
            ha_open[i] = (ha_open[i - 1] + ha_close[i - 1]) / 2.0
    ha_high = np.maximum(np.maximum(h, ha_open), ha_close)
    ha_low = np.minimum(np.minimum(l, ha_open), ha_close)

    df["ha_open"] = ha_open
    df["ha_high"] = ha_high
    df["ha_low"] = ha_low
    df["ha_close"] = ha_close

    df["ha_ema50"] = B.ema(df["ha_close"], HA_EMA_N)
    # No EMA read before bar 49: fill with ha_close so the
    # trend comparison is False (equal), never NaN.
    df["ha_ema50"] = df["ha_ema50"].fillna(df["ha_close"])

    hh = df["h"].rolling(STOCH_N, min_periods=STOCH_N).max()
    ll = df["l"].rolling(STOCH_N, min_periods=STOCH_N).min()
    rng = hh - ll
    raw_k = 100.0 * (df["c"] - ll) / rng.replace(0, np.nan)
    # Zero range (flat bars) -> neutral 50; unfilled window -> 50.
    df["stoch_k"] = raw_k.fillna(50.0)
    df["stoch_d"] = B.sma(df["stoch_k"], STOCH_D_N).fillna(50.0)
    return df
