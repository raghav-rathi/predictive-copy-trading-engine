"""CCI + MACD combo signals.

Long entry:  CCI crosses up through -100 while the MACD line is
             above its signal line.
Short entry: CCI crosses down through +100 while the MACD line is
             below its signal line.
Long exit:   CCI crosses back down through 0.
Short exit:  CCI crosses back up through 0.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cci = df["cci"]
    macd_bullish = (df["macd"] > df["macd_signal"]).fillna(False).astype(bool)
    macd_bearish = (df["macd"] < df["macd_signal"]).fillna(False).astype(bool)
    cci_up_m100 = B.crossed_above(cci, -100).fillna(False).astype(bool)
    cci_down_p100 = B.crossed_below(cci, 100).fillna(False).astype(bool)
    cci_down_0 = B.crossed_below(cci, 0).fillna(False).astype(bool)
    cci_up_0 = B.crossed_above(cci, 0).fillna(False).astype(bool)
    df["long_entry"] = (cci_up_m100 & macd_bullish).astype(bool)
    df["short_entry"] = (cci_down_p100 & macd_bearish).astype(bool)
    df["long_exit"] = cci_down_0
    df["short_exit"] = cci_up_0
    return df
