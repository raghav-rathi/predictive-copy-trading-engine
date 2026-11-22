"""Minervini Trend Template (SEPA gate) indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Trend SMAs: SMA(50), SMA(150), SMA(200) of close.
2. 200-SMA slope: SMA(200)[i] - SMA(200)[i-720]. 720 bars on 1h is
   ~1 month, the article's "200 SMA rising for at least 1 month".
3. 52-week high/low proxy: expanding max of high / expanding min of
   low over all bars seen so far. The backtest window (~8 months)
   is SHORTER than 52 weeks, so this is the longest trailing
   high/low available, not a true 52-week window — the gate is
   therefore weaker than the original (see CALIBRATION.md).
4. Momentum filter: RSI(14) > 55 stands in for the article's
   Relative Strength rating >= 70 (no crypto equivalent), exactly
   as the MQL5 article implements it.
5. Breakout level: trailing 20-bar high/low of PRIOR bars only
   (high shifted by 1, then rolling 20 max), so a close above it
   is a genuine breakout from a tight base, not a same-bar high.

Long gate (ALL eight conditions):
    c > SMA150 and c > SMA200
    SMA150 > SMA200
    SMA200 rising over trailing 720 bars
    SMA50 > SMA150 and SMA50 > SMA200
    c > SMA50
    c >= 1.25 * trailing low   (>= 25% above the 52-week low)
    c >= 0.75 * trailing high  (within 25% of the 52-week high)
    RSI(14) > 55
Short gate is the exact mirror (builder-added):
    c < SMA150 and c < SMA200, SMA150 < SMA200, SMA200 falling
    over 720 bars, SMA50 below both, c < SMA50,
    c <= 0.75 * trailing high, c <= 1.25 * trailing low, RSI < 45.

Columns:
    sma50, sma150, sma200, sma200_slope720, trail_high, trail_low,
    rsi14, donch_high20, donch_low20, gate_long, gate_short, atr

No lookahead: every rolling/expanding/shifted quantity reads bars
<= i, and the Donchian level excludes bar i itself.
"""

import pandas as pd

from strategies import base as B

SLOPE_BARS = 720      # ~1 month on 1h bars
LOW_PREMIUM = 1.25    # >= 25% above the 52-week low
HIGH_WITHIN = 0.75    # within 25% of the 52-week high
RSI_LONG = 55.0       # article's RS-rating proxy gate
RSI_SHORT = 45.0      # mirror gate
BREAKOUT_BARS = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    sma50 = B.sma(c, 50)
    sma150 = B.sma(c, 150)
    sma200 = B.sma(c, 200)
    df["sma50"] = sma50
    df["sma150"] = sma150
    df["sma200"] = sma200
    df["sma200_slope720"] = sma200 - sma200.shift(SLOPE_BARS)
    # 52-week high/low proxy: longest trailing window available.
    df["trail_high"] = h.expanding(min_periods=1).max()
    df["trail_low"] = l.expanding(min_periods=1).min()
    df["rsi14"] = B.rsi(c, 14)
    df["donch_high20"] = h.shift(1).rolling(BREAKOUT_BARS, min_periods=BREAKOUT_BARS).max()
    df["donch_low20"] = l.shift(1).rolling(BREAKOUT_BARS, min_periods=BREAKOUT_BARS).min()
    df["atr"] = B.atr(h, l, c, 14)

    gate_long = (
        (c > sma150) & (c > sma200)
        & (sma150 > sma200)
        & (df["sma200_slope720"] > 0)
        & (sma50 > sma150) & (sma50 > sma200)
        & (c > sma50)
        & (c >= LOW_PREMIUM * df["trail_low"])
        & (c >= HIGH_WITHIN * df["trail_high"])
        & (df["rsi14"] > RSI_LONG)
    )
    gate_short = (
        (c < sma150) & (c < sma200)
        & (sma150 < sma200)
        & (df["sma200_slope720"] < 0)
        & (sma50 < sma150) & (sma50 < sma200)
        & (c < sma50)
        & (c <= HIGH_WITHIN * df["trail_high"])
        & (c <= LOW_PREMIUM * df["trail_low"])
        & (df["rsi14"] < RSI_SHORT)
    )
    df["gate_long"] = gate_long.fillna(False).astype(bool)
    df["gate_short"] = gate_short.fillna(False).astype(bool)
    return df
