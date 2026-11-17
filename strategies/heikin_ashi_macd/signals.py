"""Heikin Ashi + MACD momentum filter signals.

Long entry:  MACD histogram crosses above 0 AND the Heikin Ashi
             candle is bullish (HA close > HA open).
Short entry: MACD histogram crosses below 0 AND the Heikin Ashi
             candle is bearish (HA close < HA open).
Long exit:   MACD histogram crosses below 0 (opposite zero-cross).
Short exit:  MACD histogram crosses above 0 (opposite zero-cross).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hist = df["macd_hist"]
    cross_up = B.crossed_above(hist, 0).fillna(False).astype(bool)
    cross_down = B.crossed_below(hist, 0).fillna(False).astype(bool)
    ha_bullish = (df["ha_c"] > df["ha_o"]).fillna(False).astype(bool)
    ha_bearish = (df["ha_c"] < df["ha_o"]).fillna(False).astype(bool)
    df["long_entry"] = (cross_up & ha_bullish).astype(bool)
    df["short_entry"] = (cross_down & ha_bearish).astype(bool)
    df["long_exit"] = cross_down
    df["short_exit"] = cross_up
    return df
