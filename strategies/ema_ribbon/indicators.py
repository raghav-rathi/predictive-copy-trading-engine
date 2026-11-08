"""EMA ribbon indicators.

Five exponential moving averages of close (8, 13, 21, 34, 55) plus the
ribbon spread (ema8 - ema55) / ema55, which measures how far the fast
end of the ribbon has expanded away from the slow end. All EMAs are
causal (EWMA over data through bar i), so no lookahead.
"""

import pandas as pd

from strategies.base import ema

EMA_PERIODS = (8, 13, 21, 34, 55)

INDICATOR_COLS = [
    "ema8",
    "ema13",
    "ema21",
    "ema34",
    "ema55",
    "ribbon_spread",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for n in EMA_PERIODS:
        df[f"ema{n}"] = ema(df["c"], n)
    df["ribbon_spread"] = (df["ema8"] - df["ema55"]) / df["ema55"]
    return df
