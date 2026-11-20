"""Supertrend + MACD agreement signals.

Long entry:  the first bar where Supertrend is bullish (direction +1)
             AND the MACD histogram is positive (transition into
             agreement).
Short entry: the mirror (Supertrend bearish AND histogram negative).
Long exit:   Supertrend flips bearish OR the histogram turns negative.
Short exit:  Supertrend flips bullish OR the histogram turns positive.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull = (df["supertrend_dir"] == 1) & (df["macd_hist"] > 0)
    bear = (df["supertrend_dir"] == -1) & (df["macd_hist"] < 0)
    prev_bull = bull.shift(1).fillna(False).astype(bool)
    prev_bear = bear.shift(1).fillna(False).astype(bool)
    df["long_entry"] = (bull & ~prev_bull).fillna(False).astype(bool)
    df["short_entry"] = (bear & ~prev_bear).fillna(False).astype(bool)
    df["long_exit"] = ((df["supertrend_dir"] == -1)
                       | (df["macd_hist"] < 0)).fillna(False).astype(bool)
    df["short_exit"] = ((df["supertrend_dir"] == 1)
                        | (df["macd_hist"] > 0)).fillna(False).astype(bool)
    return df
