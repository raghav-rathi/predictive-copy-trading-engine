"""J.M. Hurst FLD signals.

Entry: on the bar the cascade first aligns.
  long:  close > FLD20 AND FLD20 > FLD40 > FLD80 (bullish cascade)
  short: close < FLD20 AND FLD20 < FLD40 < FLD80 (bearish cascade)
Exit: price crosses back through the shortest FLD (FLD20) the other way.
  long exit:  close crosses below FLD20
  short exit: close crosses above FLD20
Risk-level exits (2xATR stop, 72-bar max hold) come from risk.py.
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    f20 = df["fld_20"]
    f40 = df["fld_40"]
    f80 = df["fld_80"]
    bull = (c > f20) & (f20 > f40) & (f40 > f80)
    bear = (c < f20) & (f20 < f40) & (f40 < f80)
    # enter on the transition into the cascade, not every bar it holds
    df["long_entry"] = (bull & ~bull.shift(1).fillna(False)).fillna(False)
    df["short_entry"] = (bear & ~bear.shift(1).fillna(False)).fillna(False)
    df["long_exit"] = B.crossed_below(c, f20).fillna(False)
    df["short_exit"] = B.crossed_above(c, f20).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
