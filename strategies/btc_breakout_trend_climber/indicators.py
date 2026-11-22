"""BTC Breakout Trend Climber indicators (causal, no lookahead).

Pipeline, computed bar by bar using only data through bar i:

1. 25-day Donchian channel on 1h bars: the highest high / lowest
   low of the PRIOR 600 bars (rolling window shifted by one, so the
   current bar can never trigger its own breakout — a breakout
   means the close cleared a level set entirely by past bars).
2. Bollinger Bands (50-period, 2.1 sigma) with an EMA-based mid
   (the QuantConnect source uses an EMA mid, unlike the SMA mid in
   ``strategies.base.bollinger``): mid = EMA(close, 50),
   upper/lower = mid +/- 2.1 * rolling-50 standard deviation.
3. ATR(5), ATR(10), ATR(15) for the source's staged stop/trail
   (see risk.py / CALIBRATION.md for how the single-ATR-window
   harness maps them).

Columns:

    donch_high_600 -- highest high of the prior 600 bars
    donch_low_600  -- lowest low of the prior 600 bars
    bb_mid / bb_upper / bb_lower -- EMA-based Bollinger Bands (50, 2.1)
    atr5 / atr10 / atr15 -- Wilder ATR at the three source windows
    atr -- ATR(10), the risk layer's window

No lookahead: every rolling window is trailing (includes bar i,
excludes later bars) and the Donchian levels are shifted by one
bar, so no value on bar i reads a future bar.
"""

import pandas as pd

from strategies import base as B

DONCH_N = 600          # 25 days on 1h bars
BB_N = 50
BB_K = 2.1
ATR_SHORT = 5
ATR_MID = 10
ATR_LONG = 15


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Prior-600-bar Donchian levels: shift(1) so bar i's own high/low
    # cannot set the level bar i must break.
    df["donch_high_600"] = (
        df["h"].rolling(DONCH_N, min_periods=DONCH_N).max().shift(1)
    )
    df["donch_low_600"] = (
        df["l"].rolling(DONCH_N, min_periods=DONCH_N).min().shift(1)
    )
    bb_mid = B.ema(df["c"], BB_N)
    bb_sd = df["c"].rolling(BB_N, min_periods=BB_N).std()
    df["bb_mid"] = bb_mid
    df["bb_upper"] = bb_mid + BB_K * bb_sd
    df["bb_lower"] = bb_mid - BB_K * bb_sd
    df["atr5"] = B.atr(df["h"], df["l"], df["c"], ATR_SHORT)
    df["atr10"] = B.atr(df["h"], df["l"], df["c"], ATR_MID)
    df["atr15"] = B.atr(df["h"], df["l"], df["c"], ATR_LONG)
    df["atr"] = df["atr10"]
    return df
