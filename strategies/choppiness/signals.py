"""Choppiness-regime Donchian signals.

long_entry  = Donchian(20) high breakout while CHOP < 38.2 (trending)
short_entry = Donchian(20) low breakout while CHOP < 38.2
long_exit   = CHOP crosses above 61.8 (regime turned to chop) OR close
              back below the Donchian midline
short_exit  = CHOP crosses above 61.8 OR close back above the midline
The regime filter is the edge: breakouts are only taken when the
market is actually trending.
Execution next-bar-open per the harness contract.
"""

import pandas as pd

from strategies.choppiness import indicators as I


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hi = df[f"dc_high_{I.DONCHIAN_N}"]
    lo = df[f"dc_low_{I.DONCHIAN_N}"]
    mid = df["dc_mid"]
    trending = df["trending"]
    c = df["c"]
    long_bo = (c > hi.shift(1)) & trending
    short_bo = (c < lo.shift(1)) & trending
    chop_exit = df["choppy"]
    df["long_entry"] = long_bo.fillna(False)
    df["short_entry"] = short_bo.fillna(False)
    df["long_exit"] = (chop_exit | (c < mid)).fillna(False)
    df["short_exit"] = (chop_exit | (c > mid)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].astype(bool)
    return df
