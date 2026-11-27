"""Multi-timeframe helpers: resample 1h bars to 4h, causally.

``resample_4h`` groups 1h bars into UTC-aligned 4h blocks
(00/04/08/12/16/20 UTC): o = first open, h = max high, l = min low,
c = last close, v = summed volume, t = block open (ms).

``macd_4h_aligned`` computes MACD(12, 26, 9) on the 4h closes and maps it
back onto the 1h grid using only COMPLETED 4h bars: a 1h bar opening at
time ``t`` sees the 4h bar that closed at or before ``t`` (the block
starting at ``t - 4h`` or earlier). A 1h bar inside the first, still-open
4h block therefore sees NaN until the first 4h bar completes. No
lookahead: the mapping is a backward as-of join on the 4h bar's close
time, so later 1h bars can never change an earlier bar's 4h values.
"""

from __future__ import annotations

import pandas as pd

from strategies.base import macd

FOUR_H_MS = 4 * 3_600_000


def resample_4h(df: pd.DataFrame) -> pd.DataFrame:
    """Resample a 1h OHLCV frame to UTC-aligned 4h bars."""
    out = (
        df.assign(_block=(df["t"] // FOUR_H_MS) * FOUR_H_MS)
        .groupby("_block", sort=True)
        .agg(t=("_block", "first"), o=("o", "first"), h=("h", "max"),
             l=("l", "min"), c=("c", "last"), v=("v", "sum"))
        .reset_index(drop=True)
    )
    return out[["t", "o", "h", "l", "c", "v"]]


def macd_4h_aligned(df: pd.DataFrame, fast: int = 12, slow: int = 26,
                    signal: int = 9) -> pd.DataFrame:
    """Add 4h MACD columns to a 1h frame, aligned to completed 4h bars.

    Columns added: ``macd_4h``, ``macd_signal_4h``, ``macd_hist_4h``.
    """
    df = df.copy()
    bars4 = resample_4h(df)
    m = macd(bars4["c"], fast, slow, signal)
    bars4 = bars4.assign(
        macd_4h=m["macd"].to_numpy(),
        macd_signal_4h=m["macd_signal"].to_numpy(),
        macd_hist_4h=m["macd_hist"].to_numpy(),
        # a 4h bar is usable from the moment it closes
        avail_t=bars4["t"].to_numpy() + FOUR_H_MS,
    )
    merged = pd.merge_asof(
        df[["t"]].sort_values("t"),
        bars4[["avail_t", "macd_4h", "macd_signal_4h", "macd_hist_4h"]]
        .sort_values("avail_t"),
        left_on="t",
        right_on="avail_t",
        direction="backward",
    )
    for col in ("macd_4h", "macd_signal_4h", "macd_hist_4h"):
        df[col] = merged[col].to_numpy()
    return df
