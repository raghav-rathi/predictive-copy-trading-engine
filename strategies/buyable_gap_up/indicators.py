"""Morales & Kacher Buyable Gap-Up (BGU) indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Gap: open[i] - close[i-1], measured against ATR(40) known
   through bar i-1 (atr40.shift(1)) — the gap is set at bar i's
   open, so the threshold must not use bar i's own range.
   Gap-up:   o - prev_c >= 0.75 * ATR(40)
   Gap-down: o - prev_c <= -0.75 * ATR(40)
2. Volume: v[i] vs the trailing 1,200-bar average volume through
   bar i-1 (50 trading days x 24 bars on 1h). High volume is
   v >= 1.5x that average.
3. Trend: price above SMA(50) and above SMA(200) (uptrend /
   constructive consolidation); the mirror is below both.
4. ATR(14) for the risk layer; SMA(240) is the 10-day moving
   average used for the exit (see signals.py).

Long setup:
    gap-up AND volume >= 1.5x 1200-bar average AND c > SMA50
    AND c > SMA200
Short setup is the mirror (builder-added):
    gap-down AND volume >= 1.5x AND c < SMA50 AND c < SMA200

Columns:
    atr40, gap, gap_up, gap_down, vol_avg1200, vol_ratio,
    sma50, sma200, sma240, trend_up, trend_down,
    long_setup, short_setup, atr

No lookahead: the gap threshold and volume average both exclude
bar i; the setup is evaluated on bar i's close and executed at
bar i+1's open per the house convention.
"""

import pandas as pd

from strategies import base as B

ATR_N = 40
GAP_ATR_MULT = 0.75
VOL_AVG_BARS = 1200   # 50 days x 24 bars on 1h
VOL_MULT = 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, o, h, l, v = df["c"], df["o"], df["h"], df["l"], df["v"]

    atr40 = B.atr(h, l, c, ATR_N)
    df["atr40"] = atr40
    prev_c = c.shift(1)
    df["gap"] = o - prev_c
    atr40_prev = atr40.shift(1)
    df["gap_up"] = (df["gap"] >= GAP_ATR_MULT * atr40_prev).fillna(False).astype(bool)
    df["gap_down"] = (df["gap"] <= -GAP_ATR_MULT * atr40_prev).fillna(False).astype(bool)

    vol_avg = v.shift(1).rolling(VOL_AVG_BARS, min_periods=VOL_AVG_BARS).mean()
    df["vol_avg1200"] = vol_avg
    df["vol_ratio"] = v / vol_avg

    sma50 = B.sma(c, 50)
    sma200 = B.sma(c, 200)
    df["sma50"] = sma50
    df["sma200"] = sma200
    df["sma240"] = B.sma(c, 240)
    df["atr"] = B.atr(h, l, c, 14)

    df["trend_up"] = ((c > sma50) & (c > sma200)).fillna(False).astype(bool)
    df["trend_down"] = ((c < sma50) & (c < sma200)).fillna(False).astype(bool)

    high_vol = (df["vol_ratio"] >= VOL_MULT).fillna(False)
    df["long_setup"] = (df["gap_up"] & high_vol & df["trend_up"]).astype(bool)
    df["short_setup"] = (df["gap_down"] & high_vol & df["trend_down"]).astype(bool)
    return df
