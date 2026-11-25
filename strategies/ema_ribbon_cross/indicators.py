"""EMA ribbon expansion indicators (Guppy-style stack, 8/13/21/34/55).

A ribbon of five EMAs. When the ribbon is compressed (its width at
a 20-bar minimum) and then expands with the EMAs fully aligned, the
move has room to run: compression is the coiled spring, alignment
is the direction.

Columns:
    ema8, ema13, ema21, ema34, ema55 -- EMAs of close
    ribbon_width -- (EMA8 - EMA55) / EMA55
    compression  -- |ribbon_width| at its 20-bar minimum
    comp_recent  -- compression true within the last 3 bars
    aligned_bull -- EMA8 > EMA13 > EMA21 > EMA34 > EMA55
    aligned_bear -- EMA8 < EMA13 < EMA21 < EMA34 < EMA55

No lookahead: every column is a causal EMA / rolling minimum /
comparison of bars up to and including the current bar.
"""

import pandas as pd

from strategies import base as B

PERIODS = (8, 13, 21, 34, 55)
COMPRESSION_WINDOW = 20  # shipped default
COMPRESSION_RECENT = 3   # bars


def add_indicators(
    df: pd.DataFrame,
    compression_window: int = COMPRESSION_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    for n in PERIODS:
        df[f"ema{n}"] = B.ema(df["c"], n)
    df["ribbon_width"] = (df["ema8"] - df["ema55"]) / df["ema55"]
    abs_w = df["ribbon_width"].abs()
    df["compression"] = abs_w == abs_w.rolling(
        compression_window, min_periods=compression_window
    ).min()
    df["comp_recent"] = (
        df["compression"].rolling(COMPRESSION_RECENT, min_periods=1).max() > 0
    )
    df["aligned_bull"] = (
        (df["ema8"] > df["ema13"])
        & (df["ema13"] > df["ema21"])
        & (df["ema21"] > df["ema34"])
        & (df["ema34"] > df["ema55"])
    )
    df["aligned_bear"] = (
        (df["ema8"] < df["ema13"])
        & (df["ema13"] < df["ema21"])
        & (df["ema21"] < df["ema34"])
        & (df["ema34"] < df["ema55"])
    )
    return df
