"""DPO zero-line crosses, trend-filtered (IncredibleCharts convention).

Longs only when the cycle turns up *inside an established uptrend*:
DPO crosses above zero while close sits above its 50-bar SMA. Shorts
only when DPO crosses below zero while close sits below the SMA --
trading with the trend, not against it. Per IncredibleCharts, DPO
cycle crosses are too whipsawed to trade raw; the trend filter keeps
the strategy on the side of the primary drift.

    long_entry  = crossed_above(dpo, 0) & (close > sma_ma)
    short_entry = crossed_below(dpo, 0) & (close < sma_ma)

Exits are the opposite zero-cross regardless of the trend filter:
once in a position, a cross the other way means the cycle itself
turned, so get out even if price is still on the right side of the
SMA.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dpo = df["dpo"]
    zero = pd.Series(0.0, index=df.index)
    cross_up = crossed_above(dpo, zero).fillna(False)
    cross_dn = crossed_below(dpo, zero).fillna(False)
    uptrend = (df["c"] > df["sma_ma"]).fillna(False)
    downtrend = (df["c"] < df["sma_ma"]).fillna(False)
    df["long_entry"] = (cross_up & uptrend).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & downtrend).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
