"""Everget HalfTrend indicator (amplitude=2, channelDeviation=2).

Faithful port of the open-source TradingView HalfTrend state machine
(see README for the source). All inputs are strictly causal: extremes
and SMAs use rolling windows ending at the current bar, and the "prior
bar" high/low in the flip conditions is the previous bar's value.

Columns:
    highPrice, lowPrice -- high at the bar with the highest high, and
                            low at the bar with the lowest low, over
                            the last `amplitude` bars
    highma, lowma       -- SMA(high, amplitude), SMA(low, amplitude)
    atr100              -- Wilder ATR(100)
    atr2                -- ATR(100) / 2
    dev                 -- channelDeviation * atr2 (= ATR(100) here)
    ht_trend            -- 0 = uptrend, 1 = downtrend (HalfTrend's own
                            convention, kept verbatim)
    ht                  -- HalfTrend trend line (up or down line)
    ht_up, ht_down      -- persistent up/down line values
    atrHigh, atrLow     -- ht +/- dev (channels, documented only;
                            not used for signals)
    atr                 -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

AMPLITUDE = 2
CHANNEL_DEVIATION = 2
ATR_PERIOD = 100


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    c = df["c"]
    n = len(df)

    highPrice = h.rolling(AMPLITUDE, min_periods=AMPLITUDE).max()
    lowPrice = l.rolling(AMPLITUDE, min_periods=AMPLITUDE).min()
    highma = B.sma(h, AMPLITUDE)
    lowma = B.sma(l, AMPLITUDE)
    atr100 = B.atr(h, l, c, ATR_PERIOD)
    atr2 = atr100 / 2.0
    dev = CHANNEL_DEVIATION * atr2

    hp = highPrice.to_numpy(dtype=float)
    lp = lowPrice.to_numpy(dtype=float)
    hma = highma.to_numpy(dtype=float)
    lma = lowma.to_numpy(dtype=float)
    hv = h.to_numpy(dtype=float)
    lv = l.to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)

    trend = np.zeros(n, dtype=int)
    ht = np.full(n, np.nan)
    up_line = np.full(n, np.nan)
    down_line = np.full(n, np.nan)

    # var state, initialised as in the Pine source: trend = 0 (up),
    # nextTrend = 0, maxLowPrice = prior low (or low), minHighPrice =
    # prior high (or high); up/down start unset.
    tr = 0
    nxt = 0
    maxLow = float(lv[0]) if n else np.nan
    minHigh = float(hv[0]) if n else np.nan
    up = np.nan
    down = np.nan
    prev_trend = None

    for i in range(n):
        if not (
            np.isfinite(hp[i])
            and np.isfinite(lp[i])
            and np.isfinite(hma[i])
            and np.isfinite(lma[i])
        ):
            trend[i] = tr
            up_line[i] = up
            down_line[i] = down
            continue
        prev_low = lv[i - 1] if i > 0 else lv[i]
        prev_high = hv[i - 1] if i > 0 else hv[i]
        if nxt == 1:
            maxLow = max(lp[i], maxLow)
            if hma[i] < maxLow and cv[i] < prev_low:
                tr = 1
                nxt = 0
                minHigh = float(hp[i])
        else:
            minHigh = min(hp[i], minHigh)
            if lma[i] > minHigh and cv[i] > prev_high:
                tr = 0
                nxt = 1
                maxLow = float(lp[i])
        trend[i] = tr
        if tr == 0:
            if prev_trend is not None and prev_trend == 0:
                # Continuation: up never decreases.
                up = max(maxLow, up) if np.isfinite(up) else maxLow
            else:
                # Transition from down: init from the previous down line.
                up = down if np.isfinite(down) else maxLow
            ht[i] = up
        else:
            if prev_trend is not None and prev_trend == 1:
                # Continuation: down never increases.
                down = min(minHigh, down) if np.isfinite(down) else minHigh
            else:
                # Transition from up: init from the previous up line.
                down = up if np.isfinite(up) else minHigh
            ht[i] = down
        prev_trend = tr
        up_line[i] = up
        down_line[i] = down

    df["highPrice"] = highPrice
    df["lowPrice"] = lowPrice
    df["highma"] = highma
    df["lowma"] = lowma
    df["atr100"] = atr100
    df["atr2"] = atr2
    df["dev"] = dev
    df["ht_trend"] = trend
    df["ht"] = ht
    df["ht_up"] = up_line
    df["ht_down"] = down_line
    df["atrHigh"] = ht + dev.to_numpy(dtype=float)
    df["atrLow"] = ht - dev.to_numpy(dtype=float)
    df["atr"] = B.atr(h, l, c, 14)
    return df
