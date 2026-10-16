"""Ehlers Fisher Transform reversal indicators.

John Ehlers, "The Fisher Transform" (Technical Analysis of Stocks &
Commodities). The 10-bar normalized price position is recursively smoothed
(value_i = 0.66*(2*raw_i-1) + 0.34*value_{i-1}, exactly an EMA with
alpha=0.66) and clipped to [-0.999, 0.999], then Fisher-transformed
(0.5*ln((1+value)/(1-value))) and polished with an alpha=0.5 EMA. Trigger is
the fisher series lagged one bar. ADX(14) supports the gated entry variant.
All computations are causal (no lookahead).
"""

import numpy as np
import pandas as pd

from strategies import base as B

N = 10
VALUE_ALPHA = 0.66  # Ehlers recursion: value_i = 0.66*(2*raw_i-1) + 0.34*value_{i-1}
FISHER_ALPHA = 0.5  # fisher_i = 0.5*fr_i + 0.5*fisher_{i-1}
VALUE_CLIP = 0.999  # keeps (1+value)/(1-value) finite and positive
ADX_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    lo = df["l"].rolling(N, min_periods=N).min()
    hi = df["h"].rolling(N, min_periods=N).max()
    rng = (hi - lo).replace(0, np.nan)
    raw = (df["c"] - lo) / rng
    value = (2.0 * raw - 1.0).ewm(alpha=VALUE_ALPHA, adjust=False, min_periods=N).mean()
    value = value.clip(-VALUE_CLIP, VALUE_CLIP)
    with np.errstate(divide="ignore", invalid="ignore"):
        fr = 0.5 * np.log((1.0 + value) / (1.0 - value))
    fr = fr.replace([np.inf, -np.inf], 0.0)  # belt-and-braces; the clip already prevents this
    fisher = fr.ewm(alpha=FISHER_ALPHA, adjust=False, min_periods=N).mean()
    df["fisher"] = fisher
    df["fisher_trigger"] = fisher.shift(1)
    df["adx14"] = B.adx(df["h"], df["l"], df["c"], ADX_N)["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
