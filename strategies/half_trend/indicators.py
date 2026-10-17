"""HalfTrend indicators (open-source everget/TradingView implementation).

Mechanism: over the last `amplitude` bars take the bar with the highest
high (highPrice) and the bar with the lowest low (lowPrice); channel
deviation = channelDeviation * ATR(atr_len)/2. A single stateful trend
line trails below price in uptrends (lowPrice - dev) and above price in
downtrends (highPrice + dev); the trend flips when price closes through
the line. Only amplitude-lookback extremes and causal ATR are used.
"""

import numpy as np
import pandas as pd

from strategies import base as B

AMPLITUDE = 50      # bars for the high/low extreme search
ATR_LEN = 100       # ATR length (halved, per the original)
DEV_MULT = 2.0      # channel deviation multiplier


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    c = df["c"].to_numpy()
    n = len(df)

    high_price = pd.Series(h).rolling(AMPLITUDE, min_periods=AMPLITUDE).max().to_numpy()
    low_price = pd.Series(l).rolling(AMPLITUDE, min_periods=AMPLITUDE).min().to_numpy()
    atr2 = B.atr(df["h"], df["l"], df["c"], ATR_LEN).to_numpy() / 2.0
    dev = DEV_MULT * atr2

    trend = np.full(n, np.nan)
    ht = np.full(n, np.nan)
    start = max(AMPLITUDE, ATR_LEN)
    if n > start + 1:
        trend[start] = 1.0
        ht[start] = low_price[start] - dev[start]
        for i in range(start + 1, n):
            prev_t, prev_ht = trend[i - 1], ht[i - 1]
            up = low_price[i] - dev[i]
            dn = high_price[i] + dev[i]
            if prev_t == 1:
                if c[i] < prev_ht:
                    trend[i] = -1.0
                    ht[i] = dn
                else:
                    trend[i] = 1.0
                    ht[i] = max(prev_ht, up)
            else:
                if c[i] > prev_ht:
                    trend[i] = 1.0
                    ht[i] = up
                else:
                    trend[i] = -1.0
                    ht[i] = min(prev_ht, dn)

    df["halftrend"] = ht
    df["halftrend_dir"] = trend  # +1 up / -1 down
    df["halftrend_up"] = low_price - dev
    df["halftrend_dn"] = high_price + dev
    return df
