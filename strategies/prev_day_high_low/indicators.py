"""Prior UTC-day high/low (PDH/PDL) session levels.

Crypto trades 24/7 with no true session close, so the UTC-day
boundary is the adopted session: each bar carries the high/low of
the *previous* UTC day, where stop orders are assumed to cluster.

    pdh            -- prior UTC-day high
    pdl            -- prior UTC-day low
    pd_range       -- prior-day range (pdh - pdl)
    pd_range_med20 -- 20-day median of the prior-day range
    range_ok       -- prior-day range >= 0.5x its 20-day median
                      (skip narrow-range days: they whipsaw)
    is_new_day     -- first bar of a new UTC day (midnight-flat exit)
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: every level on bar i comes from days that ended before
bar i's UTC day started.

Source: PDH/PDL breakout --
https://www.quantsapp.com/backtesting/strategies/pdh-pdl-breakout-futures-and-option-buy
"""

import numpy as np
import pandas as pd

from strategies import base as B

FILTER = 0.001       # shipped: 0.1% breakout filter beyond PDH/PDL
RANGE_MULT = 0.5     # shipped: skip if range < 0.5x its 20-day median
RANGE_MED_N = 20     # shipped: median window (days) for the range filter


def add_indicators(df: pd.DataFrame, filt: float = FILTER,
                   range_mult: float = RANGE_MULT,
                   range_med_n: int = RANGE_MED_N) -> pd.DataFrame:
    df = df.copy()
    ts = pd.to_datetime(df["t"], unit="ms", utc=True)
    day = ts.dt.floor("D")
    tmp = pd.DataFrame(
        {"day": day.to_numpy(), "h": df["h"].to_numpy(),
         "l": df["l"].to_numpy()})
    daily = tmp.groupby("day").agg(dh=("h", "max"), dl=("l", "min"))
    prev = daily.shift(1)  # yesterday's high/low, mapped onto today
    prev_range = daily["dh"] - daily["dl"]
    med = prev_range.rolling(range_med_n, min_periods=range_med_n).median().shift(1)

    day_s = pd.Series(day.to_numpy(), index=df.index)
    df["pdh"] = day_s.map(prev["dh"]).to_numpy(dtype=float)
    df["pdl"] = day_s.map(prev["dl"]).to_numpy(dtype=float)
    df["pd_range"] = df["pdh"] - df["pdl"]
    df["pd_range_med20"] = day_s.map(med).to_numpy(dtype=float)
    df["range_ok"] = (
        df["pd_range"] >= range_mult * df["pd_range_med20"]).fillna(False)
    df["is_new_day"] = day_s.ne(day_s.shift(1)).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
