"""Tasuki gap pattern indicators (causal, no lookahead).

Three-candle continuation (Steve Nison; Investopedia's upside
tasuki gap definition), with one continuous-market adaptation
(see below). The textbook rule has the third candle close
inside the gap between the first candle's close and the second
candle's open — but on a 24/7 crypto market that gap is a
tick-size artifact (median 0.3–0.9% of one candle's range in
this window; the literal rule fires ZERO times in ~16,300
bars, diagnosed in CALIBRATION.md). The adaptation keeps the
pattern's economics — a counter-color pullback that does NOT
close the gap — and widens only the retracement bound from the
second candle's open to its close:

    Upside (long): bar i-2 white, bar i-1 white gapping up
        (o[i-1] > c[i-2]), bar i black whose open lies inside
        bar i-1's body (o[i-1] <= o[i] <= c[i-1]) and whose
        close retraces below bar i-1's close but holds above
        bar i-2's close (c[i-2] < c[i] < c[i-1]) — the gap is
        not closed. First two bodies each at least half their
        range. Continuation filter: the first candle's close
        sits above the close 5 bars earlier (an existing
        uptrend).
    Downside (short): mirror, with a downtrend filter
        (c[i-2] < c[i-7]).

The pattern completes on bar i, so it uses only bars i-2..i.

Columns:
    tasuki_dir -- +1 on an upside tasuki bar, -1 on a downside
                  tasuki bar, else 0
    atr        -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

MIN_BODY_FRAC = 0.5
TREND_BARS = 5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"].to_numpy(dtype=float)
    c = df["c"].to_numpy(dtype=float)
    h = df["h"].to_numpy(dtype=float)
    l = df["l"].to_numpy(dtype=float)
    n = len(df)

    body = c - o
    rng = np.maximum(h - l, 0.0)
    strong = np.abs(body) >= MIN_BODY_FRAC * rng

    direction = np.zeros(n, dtype=int)
    if n >= TREND_BARS + 3:
        # start at TREND_BARS + 2 so a - TREND_BARS never wraps
        # around to the end of the array (which would be lookahead)
        i1 = np.arange(TREND_BARS + 2, n)  # pattern's third-bar index
        a, b, cc = i1 - 2, i1 - 1, i1
        up = (
            (c[a] > o[a]) & (c[b] > o[b])
            & (o[b] > c[a])
            & strong[a] & strong[b]
            & (c[cc] < o[cc])
            & (o[cc] >= o[b]) & (o[cc] <= c[b])
            & (c[cc] > c[a]) & (c[cc] < c[b])
            & (c[a] > c[a - TREND_BARS])
        )
        down = (
            (c[a] < o[a]) & (c[b] < o[b])
            & (o[b] < c[a])
            & strong[a] & strong[b]
            & (c[cc] > o[cc])
            & (o[cc] <= o[b]) & (o[cc] >= c[b])
            & (c[cc] < c[a]) & (c[cc] > c[b])
            & (c[a] < c[a - TREND_BARS])
        )
        direction[i1[up]] = 1
        direction[i1[down]] = -1

    df["tasuki_dir"] = direction
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
