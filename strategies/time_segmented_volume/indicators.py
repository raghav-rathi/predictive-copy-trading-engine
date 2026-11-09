"""Worden time segmented volume (TSV) indicators.

Per-bar signed money flow = (close - close[1]) * volume, i.e. the
bar's close-to-close move weighted by how much traded. TSV(18) is
the rolling 18-bar sum of that flow: positive TSV means net
accumulation over the window, negative means net distribution.
The first bar's flow is 0 (no prior close). All windows end at bar
i, so no lookahead.
"""

import pandas as pd

PERIOD = 18

INDICATOR_COLS = [
    "tsv_flow",
    "tsv",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    flow = (df["c"] - df["c"].shift(1)).fillna(0.0) * df["v"]
    df["tsv_flow"] = flow
    df["tsv"] = flow.rolling(PERIOD, min_periods=PERIOD).sum()
    return df
