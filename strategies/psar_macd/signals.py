"""Parabolic SAR + MACD agreement signals.

Long entry:  PSAR flips to below price (direction -1 -> +1) AND the
             MACD line is above its signal on that bar.
Short entry: PSAR flips to above price (direction +1 -> -1) AND the
             MACD line is below its signal on that bar.
Long exit:   opposite PSAR flip OR MACD line crosses below signal.
Short exit:  opposite PSAR flip OR MACD line crosses above signal.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_dir = df["psar_dir"].shift(1)
    flip_long = (df["psar_dir"] == 1) & (prev_dir == -1)
    flip_short = (df["psar_dir"] == -1) & (prev_dir == 1)
    macd_bull = df["macd"] > df["macd_signal"]
    macd_bear = df["macd"] < df["macd_signal"]
    df["long_entry"] = (flip_long & macd_bull).fillna(False).astype(bool)
    df["short_entry"] = (flip_short & macd_bear).fillna(False).astype(bool)
    df["long_exit"] = (flip_short
                       | B.crossed_below(df["macd"], df["macd_signal"])
                       ).fillna(False).astype(bool)
    df["short_exit"] = (flip_long
                        | B.crossed_above(df["macd"], df["macd_signal"])
                        ).fillna(False).astype(bool)
    return df
