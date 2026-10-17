"""Candlestick pattern detectors (Nison-style price action).

bull_engulf = bearish body then a bullish body whose body engulfs the
              prior body (open <= prior close, close >= prior open)
bear_engulf = mirror
bull_pin    = lower wick >= 2x body, body in the top third of the range,
              range >= 0.5x ATR (rejects doji-noise)
bear_pin    = mirror (upper wick)
Patterns are single-bar facts at bar i; entries execute next-bar-open.
All causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

PIN_WICK_MULT = 2.0   # wick must be >= 2x the body
MIN_RANGE_ATR = 0.5   # bar range must be >= 0.5x ATR


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o, h, l, c = df["o"], df["h"], df["l"], df["c"]
    body = (c - o).abs()
    rng = (h - l).replace(0, np.nan)
    atr_v = B.atr(h, l, c, 14)

    po, pc = o.shift(1), c.shift(1)
    pbody = (pc - po).abs()
    bull_engulf = (pc < po) & (c > o) & (o <= pc) & (c >= po) & (body > pbody)
    bear_engulf = (pc > po) & (c < o) & (o >= pc) & (c <= po) & (body > pbody)

    bull_wick = np.minimum(o, c) - l
    bear_wick = h - np.maximum(o, c)
    big_enough = rng >= MIN_RANGE_ATR * atr_v
    bull_pin = (bull_wick >= PIN_WICK_MULT * body) & ((c - l) / rng >= 2.0 / 3.0) & big_enough
    bear_pin = (bear_wick >= PIN_WICK_MULT * body) & ((h - c) / rng >= 2.0 / 3.0) & big_enough

    df["bull_engulf"] = bull_engulf.fillna(False)
    df["bear_engulf"] = bear_engulf.fillna(False)
    df["bull_pin"] = bull_pin.fillna(False)
    df["bear_pin"] = bear_pin.fillna(False)
    return df
