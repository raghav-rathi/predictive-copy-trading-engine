"""RSI / RSI-band signals.

    long_entry  -- RSI crosses above its lower band (leaving an
                  extreme-low RSI reading)
    short_entry -- RSI crosses below its upper band (leaving an
                  extreme-high RSI reading)
    long_exit   -- RSI crosses above its middle band
    short_exit  -- RSI crosses below its middle band

Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    le = B.crossed_above(df["rsi"], df["rsi_lower"]).fillna(False)
    se = B.crossed_below(df["rsi"], df["rsi_upper"]).fillna(False)
    lx = B.crossed_above(df["rsi"], df["rsi_mid"]).fillna(False)
    sx = B.crossed_below(df["rsi"], df["rsi_mid"]).fillna(False)
    df["long_entry"] = le.astype(bool)
    df["short_entry"] = se.astype(bool)
    df["long_exit"] = lx.astype(bool)
    df["short_exit"] = sx.astype(bool)
    return df
