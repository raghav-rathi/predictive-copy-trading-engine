"""Volume-weighted MACD signals.

Long on a MACD-line cross above its signal line with a positive
histogram while the volume-weighted price sits above the prior-bar
SMA(50) of close; short on the mirror. Exits are the opposite MACD
cross. All comparisons use the prior bar's SMA(50) so the current
close is never compared against an indicator computed from itself.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sma_prev = df["sma50"].shift(1)
    cross_up = B.crossed_above(df["vw_macd"], df["vw_signal"])
    cross_down = B.crossed_below(df["vw_macd"], df["vw_signal"])
    df["long_entry"] = (cross_up & (df["vw_hist"] > 0) & (df["vw_price"] > sma_prev)).astype(bool)
    df["short_entry"] = (cross_down & (df["vw_hist"] < 0) & (df["vw_price"] < sma_prev)).astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
