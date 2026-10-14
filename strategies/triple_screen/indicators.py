"""Alexander Elder Triple Screen indicators (Trading for a Living, 1993).

Screen 1 (the tide): resample 1h bars to 4h, take MACD(12,26,9) on the 4h
closes. Histogram slope > 0 = rising tide (buy dips only), < 0 = falling
tide (sell rallies only). The tide for each 1h bar is taken from the most
recent *closed* 4h bar (shifted one 4h bar before forward-filling) so no
incomplete-bar lookahead leaks in.

Screen 2 (the wave): 1h 2-period EMA of Force Index, reused from our
force_index package (same branch, no duplicated code).

Screen 3 is executed in signals.py (buy-stop approximation).
"""

import pandas as pd

from strategies import base as B
from strategies.force_index import indicators as fi_ind

MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def _resample_4h(df: pd.DataFrame) -> pd.DataFrame:
    g = df.assign(ts=pd.to_datetime(df["t"], unit="ms", utc=True))
    g = g.set_index("ts").sort_index()
    r = g.resample("4h").agg(
        {"o": "first", "h": "max", "l": "min", "c": "last", "v": "sum", "t": "first"}
    )
    return r.dropna()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = fi_ind.add_indicators(df)          # fi_raw, fi13, fi2, atr (1h)
    df = df.copy()

    r4 = _resample_4h(df)
    m = B.macd(r4["c"], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    # histogram slope of the last CLOSED 4h bar: shift(1) before mapping
    slope_closed = (m["macd_hist"] - m["macd_hist"].shift(1)).shift(1)
    slope_by_t = pd.Series(slope_closed.to_numpy(), index=r4["t"].to_numpy())
    df["tide_slope"] = df["t"].map(slope_by_t).ffill()
    df["tide_up"] = df["tide_slope"] > 0
    df["tide_dn"] = df["tide_slope"] < 0
    return df
