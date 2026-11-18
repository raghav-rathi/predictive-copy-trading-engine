"""Bollinger band tag + MACD cross signals.

Long entry:  MACD crosses above its signal line on this bar AND
             the low touched or pierced the lower band within the
             last 3 bars (min low of bars i-2..i <= bb_lower[i],
             using the current bar's band value).
Short entry: MACD crosses below its signal line AND the high
             touched or pierced the upper band within the last
             3 bars (max high of bars i-2..i >= bb_upper[i]).
Long exit:   MACD crosses below its signal line OR close above
             the upper band (reached the opposite band).
Short exit:  MACD crosses above its signal line OR close below
             the lower band.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = B.crossed_above(df["macd"], df["macd_signal"]).fillna(False)
    cross_dn = B.crossed_below(df["macd"], df["macd_signal"]).fillna(False)
    low_touch = (df["l"].rolling(3, min_periods=1).min() <= df["bb_lower"]).fillna(False)
    high_touch = (df["h"].rolling(3, min_periods=1).max() >= df["bb_upper"]).fillna(False)
    df["long_entry"] = (cross_up & low_touch).astype(bool)
    df["short_entry"] = (cross_dn & high_touch).astype(bool)
    df["long_exit"] = (cross_dn | (df["c"] > df["bb_upper"])).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | (df["c"] < df["bb_lower"])).fillna(False).astype(bool)
    return df
