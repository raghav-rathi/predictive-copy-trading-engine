"""Oops pattern session indicators (Larry Williams).

On 1h bars a trading "day" is proxied by a 24-bar session. The prior
session's range is taken from the *completed* prior 24-bar window only --
no lookahead:

    prev_day_high = rolling(24).max(high).shift(24)
    prev_day_low  = rolling(24).min(low).shift(24)

A "gap" is a bar whose open prints beyond the completed prior session's
extreme:

    gap_down = open < prev_day_low
    gap_up   = open > prev_day_high

Columns:

    prev_day_high / prev_day_low -- completed prior 24-bar session range
    gap_down / gap_up            -- boolean gap flags
    atr                          -- Wilder ATR(14) for the risk layer

No lookahead: the shift(24) pushes the rolling window one full session
back, so at bar j the range uses bars j-47..j-24 only. The first
fully-formed values arrive at bar 47 (0-based), inside WARMUP=48.

Note: crypto trades 24/7 with no true opens, so a "gap" here is really
a bar opening beyond the prior session's extreme -- the 1h-bar
adaptation of Williams' opening gap. They are rarer than on equities
and coincide with fresh 24-bar breakdowns/breakouts at the open.
"""

import pandas as pd

from strategies import base as B

SESSION = 24  # bars per proxied "day"; fixed a priori


def add_indicators(df: pd.DataFrame, session: int = SESSION) -> pd.DataFrame:
    df = df.copy()
    df["prev_day_high"] = (
        df["h"].rolling(session).max().shift(session)
    )
    df["prev_day_low"] = (
        df["l"].rolling(session).min().shift(session)
    )
    df["gap_down"] = (df["o"] < df["prev_day_low"]).fillna(False).astype(bool)
    df["gap_up"] = (df["o"] > df["prev_day_high"]).fillna(False).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
