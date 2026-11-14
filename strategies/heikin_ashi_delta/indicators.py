"""Heikin Ashi delta momentum (classic).

    HA_close = (o + h + l + c) / 4
    HA_open  = (prev HA_open + prev HA_close) / 2   (seeded with the first bar's open)
    delta    = HA_close - HA_open

The sign of delta is the Heikin Ashi candle colour: positive = green
(bullish), negative = red (bearish). A delta sign change is a smoothed
momentum turn — the averaging filters one-bar noise, at the cost of
lag (see README). Columns:

    ha_open   -- Heikin Ashi open (recursive average)
    ha_close  -- Heikin Ashi close
    ha_delta  -- ha_close - ha_open (the momentum signal)
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: HA_open on bar j uses only bars through j-1 plus bar j's
own OHLC for HA_close; delta on bar j uses data through bar j only.
The recursion is computed with an explicit loop (vectorising the
recurrence is not possible — each HA_open depends on the previous one).
"""

import numpy as np
import pandas as pd

from strategies import base as B


def heikin_ashi(o: pd.Series, h: pd.Series, l: pd.Series,
                c: pd.Series) -> pd.DataFrame:
    """Heikin Ashi open/close/delta from OHLC series."""
    ha_close = (o + h + l + c) / 4.0
    ha_close_v = ha_close.to_numpy(dtype=float)
    o_v = o.to_numpy(dtype=float)
    n = len(ha_close_v)
    ha_open_v = np.empty(n, dtype=float)
    ha_open_v[0] = o_v[0]  # seed with the first bar's open
    for i in range(1, n):
        ha_open_v[i] = (ha_open_v[i - 1] + ha_close_v[i - 1]) / 2.0
    ha_open = pd.Series(ha_open_v, index=o.index)
    return pd.DataFrame({
        "ha_open": ha_open,
        "ha_close": ha_close,
        "ha_delta": ha_close - ha_open,
    })


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ha = heikin_ashi(df["o"], df["h"], df["l"], df["c"])
    df["ha_open"] = ha["ha_open"]
    df["ha_close"] = ha["ha_close"]
    df["ha_delta"] = ha["ha_delta"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
