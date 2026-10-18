"""Victor Sperandeo 1-2-3 indicators (Trader Vic: Methods of a Wall Street Master).

5-bar fractal pivots: a swing low at bar j is the strict minimum of
low[j-2..j+2]; a swing high the strict maximum of high[j-2..j+2]. The
pivot flags sit at their formation bar; a pivot is only *confirmed*
(and therefore only consumed by signals.py) once bars through j+2
exist, i.e. signals at bar i use pivots with formation bar <= i-2 --
no lookahead.

The trend-line fit itself lives in signals.py (state machine); the
columns here are the pivot primitives plus ATR for the risk proxy.
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    l, h = df["l"], df["h"]
    df["piv_low"] = (
        (l < l.shift(1)) & (l < l.shift(2)) & (l < l.shift(-1)) & (l < l.shift(-2))
    ).fillna(False)
    df["piv_high"] = (
        (h > h.shift(1)) & (h > h.shift(2)) & (h > h.shift(-1)) & (h > h.shift(-2))
    ).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
