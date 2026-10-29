"""Stochastic Pop indicators (Linda Raschke, Street Smarts).

Raschke's Pop is a breakout-continuation setup, not an oscillator
cross: price breaks out of its recent range WHILE the fast
stochastic is already pinned at an extreme. The pop says the
breakout has momentum behind it; the trade is the continuation,
not the fade. That is what separates it from stoch_hook (a
slow-stochastic cross against its trigger inside a trend bias,
with no breakout requirement).

Definitions (all causal, rolling windows use only bars through
the current close):
    fastK  -- 100 * (c - lowest(l,14)) / (highest(h,14) - lowest(l,14))
    range_high -- highest high of the prior 20 bars (excluding today)
    range_low  -- lowest low of the prior 20 bars (excluding today)
    pop_up -- fastK crosses above 80 AND close breaks above range_high
    pop_dn -- fastK crosses below 20 AND close breaks below range_low
    atr    -- Wilder ATR(14) for the risk layer

The breakout bars exclude today from the range so a close above
the prior 20-bar high is a genuine new high, not a restatement
of today's own high.
"""

import numpy as np
import pandas as pd

from strategies import base as B

K_N = 14
RANGE_N = 20
OB = 80.0
OS = 20.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hh = df["h"].rolling(K_N, min_periods=K_N).max()
    ll = df["l"].rolling(K_N, min_periods=K_N).min()
    denom = (hh - ll).replace(0, pd.NA)
    fastk = 100 * (df["c"] - ll) / denom
    df["fastK"] = fastk.fillna(50.0)
    # prior-20-bar range, excluding today
    df["range_high"] = df["h"].shift(1).rolling(RANGE_N, min_periods=RANGE_N).max()
    df["range_low"] = df["l"].shift(1).rolling(RANGE_N, min_periods=RANGE_N).min()
    k = df["fastK"]
    cross_up = B.crossed_above(k, OB).fillna(False)
    cross_dn = B.crossed_below(k, OS).fillna(False)
    breakout_up = (df["c"] > df["range_high"]).fillna(False)
    breakout_dn = (df["c"] < df["range_low"]).fillna(False)
    df["pop_up"] = (cross_up & breakout_up).fillna(False).astype(bool)
    df["pop_dn"] = (cross_dn & breakout_dn).fillna(False).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
