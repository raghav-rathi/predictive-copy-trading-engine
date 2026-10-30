"""Multi-timeframe stack: 4h trend filter + 1h EMA-cross entries.

Resampling is causal and index-based: the 1h bars are grouped every 4
consecutive bars, and a 4h bar only exists once its 4th hour has closed.
A 1h bar i therefore sees only 4h bars completed before it (groups
strictly before i//4); the in-progress 4h bar is never used. The 4h
closes feed EMA(20) and EMA(50); the 4h trend is +1 when EMA(20) is above
EMA(50), -1 when below, 0 before both EMAs are defined. The 4h EMA
values are forward-filled onto 1h bars at their last completed value.

Note on grouping: groups are formed by position in the (sorted,
deduplicated) 1h series, not by wall-clock hour, so the stack stays
well-defined even if the cache has an occasional missing hour; on the
backtest window the bars are consecutive hours, so groups align with
00/04/08/12/16/20 UTC blocks.

Columns:
    ema9, ema21   -- 1h EMAs on closes
    htf_ema20, htf_ema50 -- last completed 4h-bar EMAs (NaN until 20/50
                            completed 4h bars exist)
    htf_trend     -- +1 / -1 / 0 as above
    atr           -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

GROUP = 4
HTF_FAST = 20
HTF_SLOW = 50
FAST = 9
SLOW = 21


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    n = len(df)
    df["ema9"] = B.ema(c, FAST)
    df["ema21"] = B.ema(c, SLOW)
    # Completed 4h bars: close of every 4th 1h bar (index 3, 7, 11, ...).
    n_groups = n // GROUP
    closes_4h = pd.Series(
        [float(c.iloc[GROUP * g + GROUP - 1]) for g in range(n_groups)]
    )
    e20 = B.ema(closes_4h, HTF_FAST)
    e50 = B.ema(closes_4h, HTF_SLOW)
    htf20 = np.full(n, np.nan)
    htf50 = np.full(n, np.nan)
    for i in range(n):
        g = i // GROUP
        if g >= 1 and g - 1 < n_groups:
            htf20[i] = e20.iloc[g - 1]
            htf50[i] = e50.iloc[g - 1]
    df["htf_ema20"] = htf20
    df["htf_ema50"] = htf50
    df["htf_trend"] = np.where(
        np.isfinite(htf20) & np.isfinite(htf50) & (htf20 > htf50), 1,
        np.where(
            np.isfinite(htf20) & np.isfinite(htf50) & (htf20 < htf50), -1, 0,
        ),
    ).astype(int)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
