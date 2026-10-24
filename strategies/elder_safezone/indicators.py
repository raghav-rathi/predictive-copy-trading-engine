"""Alexander Elder SafeZone indicators (Come Into My Trading Room, 2002).

The SafeZone is Elder's volatility-based trailing stop line. For longs
it hangs below the recent highs of the lows: take the highest low of
the last N bars, then subtract a multiple of the average
counter-trend penetration — how far, on average, each bar's low
dips below the previous bar's low:

    pen_down[j]    = max(0, low[j-1] - low[j])
    avg_pen[j]     = mean(pen_down[j-9..j])
    safezone_long  = highest_low_10[j] - 2.5 * avg_pen[j]

The short line mirrors it off the highs:

    pen_up[j]       = max(0, high[j] - high[j-1])
    safezone_short  = lowest_high_10[j] + 2.5 * mean(pen_up[j-9..j])

The logic: in a healthy uptrend, pullbacks penetrate the prior
low only shallowly, so the average penetration is small and the
line hugs the lows; when a bar breaks the line, the counter-trend
move is deeper than anything normal for the last 10 bars, so the
trend is suspect. The 2.5x multiple is Elder's published default.

Columns:

    ema22          -- EMA(22) of close, the trend filter
    safezone_long  -- long-side SafeZone line
    safezone_short -- short-side SafeZone line
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n). Early
bars with incomplete windows are forward/back-filled so the only
NaN-free region starts after warmup.
"""

import pandas as pd

from strategies import base as B

EMA_N = 22        # shipped default (fixed a priori, Elder's trend EMA)
SZ_N = 10         # SafeZone lookback in bars
PEN_MULT = 2.5    # Elder's published penetration multiple


def add_indicators(df: pd.DataFrame, ema_n: int = EMA_N,
                   sz_n: int = SZ_N,
                   pen_mult: float = PEN_MULT) -> pd.DataFrame:
    df = df.copy()
    low = df["l"]
    high = df["h"]

    df["ema22"] = B.ema(df["c"], ema_n).ffill().bfill()

    highest_low = low.rolling(sz_n, min_periods=sz_n).max()
    pen_down = (low.shift(1) - low).clip(lower=0)
    avg_pen_down = pen_down.rolling(sz_n, min_periods=sz_n).mean()
    df["safezone_long"] = (highest_low - pen_mult * avg_pen_down).ffill().bfill()

    lowest_high = high.rolling(sz_n, min_periods=sz_n).min()
    pen_up = (high - high.shift(1)).clip(lower=0)
    avg_pen_up = pen_up.rolling(sz_n, min_periods=sz_n).mean()
    df["safezone_short"] = (lowest_high + pen_mult * avg_pen_up).ffill().bfill()

    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
