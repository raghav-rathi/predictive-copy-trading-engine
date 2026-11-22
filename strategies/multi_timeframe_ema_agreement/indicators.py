"""Multi-Timeframe EMA Agreement indicators (BotLab study).

Pipeline, computed bar by bar using only data through bar i:

1. 1h EMAs: EMA(9) / EMA(21) on the 1h close.
2. 4h EMAs: the 1h closes are resampled to 4h bars (UTC-anchored,
   00:00/04:00/08:00/...), the 4h close is the last 1h close of
   the bucket, and EMA(9) / EMA(21) are computed over the 4h
   closes. A 4h bar is only used once it has closed: the 1h bar
   at time t reads the 4h EMA of the most recent 4h bar whose
   start is <= t - 4h, i.e. a 4h bar covering [T, T+4h) first
   becomes visible to the 1h bar opening at T+4h — after its
   final 1h close (the bar starting T+3h, closing at T+4h) is
   known. No partial 4h bar is ever read.

No lookahead: the 1h EMAs are causal EWMs, and the 4h mapping
above only ever reaches backwards to completed 4h bars. The
appended-future-bars test in test_multi_timeframe_ema_agreement.py
verifies this directly.
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_FAST = 9
EMA_SLOW = 21
HTF_HOURS = 4


def _htf_ema(close: pd.Series, t_ms: np.ndarray, span: int) -> np.ndarray:
    """EMA(span) over 4h closes, mapped back to 1h bars causally.

    close: 1h closes; t_ms: bar open timestamps in ms. Returns an
    array aligned to the 1h bars where entry i is the EMA of the
    most recent COMPLETED 4h bar as of bar i's close. All bucket
    arithmetic is int64 nanoseconds, so no tz/dtype ambiguity.
    """
    ns_per_4h = 4 * 3600 * 10**9
    t_ns = t_ms.astype(np.int64) * 10**6
    bucket = (t_ns // ns_per_4h) * ns_per_4h
    htf_close = close.groupby(bucket).last()
    htf_ema = htf_close.ewm(span=span, adjust=False, min_periods=span).mean()
    idx = htf_ema.index.values.astype(np.int64)  # 4h bucket starts, ascending
    vals = htf_ema.to_numpy(dtype=float)
    # A 4h bar starting at S completes at S+4h; bar i (open time t)
    # may use it once S <= t - 4h.
    query = t_ns - ns_per_4h
    pos = np.searchsorted(idx, query, side="right") - 1
    out = np.full(len(close), np.nan)
    ok = pos >= 0
    out[ok] = vals[pos[ok]]
    return out


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["ema_fast_1h"] = B.ema(c, EMA_FAST)
    df["ema_slow_1h"] = B.ema(c, EMA_SLOW)
    times = df["t"].to_numpy(dtype=np.int64)
    df["ema_fast_4h"] = _htf_ema(c, times, EMA_FAST)
    df["ema_slow_4h"] = _htf_ema(c, times, EMA_SLOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
