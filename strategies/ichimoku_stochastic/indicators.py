"""Ichimoku cloud + Stochastic indicators (causal, no lookahead).

Ichimoku (9/26/52) via ``strategies.base.ichimoku``:
- Tenkan-sen: midpoint of the 9-bar high/low range.
- Kijun-sen: midpoint of the 26-bar high/low range.
- Senkou Span A: (Tenkan + Kijun) / 2, shifted +26 bars (standard
  cloud plot). Senkou Span B: midpoint of the 52-bar range,
  shifted +26 bars.
- Causality note: at bar i the shifted Senkou values derive from
  data through bar i-26, so reading them at bar i uses only past
  data. They are the *historical* cloud, not the projected cloud
  — the projected cloud 26 bars ahead is never read.
- Chikou Span is NOT computed here: ``base.ichimoku`` defines it
  as ``c.shift(-26)``, which looks 26 bars into the future. No
  signal reads it, so it is dropped entirely rather than carried.

Stochastic (14,3,3) on regular closes:
- %K = 100 * (c - LL14) / (HH14 - LL14), where LL14/HH14 are the
  lowest/highest closes of the last 14 bars including bar i.
- %D = SMA(3) of %K.
- Flat range (HH14 == LL14): %K is defined as 50.0 (neutral) so
  the column never carries NaN or infinity.
- Seeding: %K is NaN for the first 13 bars (rolling window not
  full) and is seeded to 50.0; %D is seeded to %K where its SMA
  is not yet defined. Both columns are therefore finite on every
  bar. WARMUP = 80 covers the seeding window.

Tenkan/Kijun/Senkou columns keep NaN before their windows are
full (52 + 26 bars for the cloud). Signal comparisons against
NaN are False, so no entry can fire in the unformed region.
``cloud_top`` / ``cloud_bottom`` are max/min of the two Senkou
spans.
"""

import numpy as np
import pandas as pd

from strategies import base as B

STOCH_K = 14
STOCH_D = 3


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    ich = B.ichimoku(h, l, c)
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    df["senkou_a"] = ich["senkou_a"]
    df["senkou_b"] = ich["senkou_b"]
    # Chikou Span deliberately omitted (lookahead in base.ichimoku).
    df["cloud_top"] = pd.concat([df["senkou_a"], df["senkou_b"]], axis=1).max(axis=1)
    df["cloud_bottom"] = pd.concat([df["senkou_a"], df["senkou_b"]], axis=1).min(axis=1)

    ll = c.rolling(STOCH_K, min_periods=STOCH_K).min()
    hh = c.rolling(STOCH_K, min_periods=STOCH_K).max()
    rng = hh - ll
    pct_k = 100.0 * (c - ll) / rng.replace(0, np.nan)
    # Flat 14-bar range -> neutral 50.0; first 13 bars (window not
    # full) also seeded to 50.0. Clip to [0, 100]: when the close
    # equals the 14-bar high, floating-point rounding can push the
    # ratio a hair above 1 (100.00000000000001 observed).
    pct_k = pct_k.fillna(50.0).clip(0.0, 100.0)
    df["stoch_k"] = pct_k
    df["stoch_d"] = pct_k.rolling(STOCH_D, min_periods=STOCH_D).mean().fillna(pct_k)

    df["atr14"] = B.atr(h, l, c, 14)
    return df
