"""VWMA crossover signals: long on VWMA(10) crossing above VWMA(50),
short on crossing below; exit on the opposite cross."""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["vwma_fast"], df["vwma_slow"]).astype(bool)
    df["short_entry"] = B.crossed_below(df["vwma_fast"], df["vwma_slow"]).astype(bool)
    df["long_exit"] = B.crossed_below(df["vwma_fast"], df["vwma_slow"]).astype(bool)
    df["short_exit"] = B.crossed_above(df["vwma_fast"], df["vwma_slow"]).astype(bool)
    return df
