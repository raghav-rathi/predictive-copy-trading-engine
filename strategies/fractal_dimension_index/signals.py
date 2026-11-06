"""Fractal Dimension Index signals.

Entry rule (the one chosen, documented in the README): enter when the
FDI is in the clean-trend regime (FDI(30) < 1.4) and the close crosses
SMA(20) in the trade direction. The close is compared against the
prior bar's SMA(20) so the current close is never compared against an
indicator computed from itself. Exits: FDI rises above 1.5 (choppy
regime) or the close crosses back through SMA(20).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sma_prev = df["sma20"].shift(1)
    trending = df["fdi30"] < 1.4
    cross_up = (df["c"] > sma_prev) & (df["c"].shift(1) <= sma_prev.shift(1))
    cross_down = (df["c"] < sma_prev) & (df["c"].shift(1) >= sma_prev.shift(1))
    df["long_entry"] = (trending & cross_up).astype(bool)
    df["short_entry"] = (trending & cross_down).astype(bool)
    df["long_exit"] = ((df["fdi30"] > 1.5) | (df["c"] < sma_prev)).astype(bool)
    df["short_exit"] = ((df["fdi30"] > 1.5) | (df["c"] > sma_prev)).astype(bool)
    return df
