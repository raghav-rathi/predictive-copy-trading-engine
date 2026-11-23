"""Stochastic + Bollinger %b indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. Bollinger Bands(20, 2) via base.bollinger: mid = SMA(20),
   upper/lower = mid +/- 2 * sample SD(20).
   %b = (c - lower) / (upper - lower): 0 at the lower band,
   1 at the upper band, 0.5 at the mid-band.
2. Stochastic(14, 3, 3): raw %K = 100 * (c - lowest low 14) /
   (highest high 14 - lowest low 14), smoothed with a 3-bar SMA
   to give %K; %D = 3-bar SMA of %K.
3. ATR(14) for the risk layer.

Seeding (deterministic, documented — no NaN leaks into signals):
- %b is undefined for the first 19 bars (Bollinger needs 20
  closes) and undefined when the band width is zero (flat
  market, upper == lower); both cases are seeded to 0.5, the
  neutral mid-band value. A flat market is neither oversold
  nor overbought, so 0.5 is the honest neutral seed.
- Raw %K is undefined for the first 13 bars (needs a 14-bar
  high/low window) and when the 14-bar range is zero; both
  cases are seeded to 50.0 (neutral). %K/%D are then seeded
  to 50.0 until the 3-bar smoothings have enough values
  (bars 0-1). A seeded 50/50 cannot produce a cross, so no
  signal can fire on seeded data.

Columns:
    bb_mid, bb_upper, bb_lower, bb_width, pct_b,
    stoch_k, stoch_d, atr

No lookahead: every value on bar i uses data through bar i's
close only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
STOCH_K_PERIOD = 14
STOCH_SMOOTH = 3
STOCH_D_PERIOD = 3

# Entry gates (see signals.py / CALIBRATION.md).
PCTB_OVERSOLD = 0.2
PCTB_OVERBOUGHT = 0.8
STOCH_OVERSOLD = 30.0
STOCH_OVERBOUGHT = 70.0


def stochastic(h, l, c, k_period: int = STOCH_K_PERIOD,
               smooth: int = STOCH_SMOOTH, d_period: int = STOCH_D_PERIOD):
    """Slow Stochastic(14, 3, 3). Returns %K and %D, seeded to 50.0
    where the 14-bar window is not yet available or the range is
    zero (flat market)."""
    ll = l.rolling(k_period, min_periods=k_period).min()
    hh = h.rolling(k_period, min_periods=k_period).max()
    rng = hh - ll
    raw_k = 100.0 * (c - ll) / rng.replace(0, np.nan)
    # Zero 14-bar range (flat market) -> neutral 50, not NaN/inf.
    # First k_period-1 bars (no full window yet) -> also 50.
    raw_k = raw_k.where(rng.notna() & (rng != 0), 50.0)
    k = raw_k.rolling(smooth, min_periods=smooth).mean()
    d = k.rolling(d_period, min_periods=d_period).mean()
    return pd.DataFrame({"stoch_k": k, "stoch_d": d})


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    bb = B.bollinger(c, BB_N, BB_K)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_width"] = bb["bb_width"]
    width = (bb["bb_upper"] - bb["bb_lower"]).replace(0, np.nan)
    df["pct_b"] = ((c - bb["bb_lower"]) / width).fillna(0.5)

    st = stochastic(h, l, c)
    df["stoch_k"] = st["stoch_k"].fillna(50.0)
    df["stoch_d"] = st["stoch_d"].fillna(50.0)

    df["atr"] = B.atr(h, l, c, 14)
    return df
