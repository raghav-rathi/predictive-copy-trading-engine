"""Elder Ray indicators -- Dr. Alexander Elder ("Trading for a Living").

Elder Ray decomposes the bar around a trend baseline (EMA(13)):

    ema13     = EMA(close, 13)                    [B.ema]
    bull_power = high - ema13    -- how far bulls can lift price above value
    bear_power = low  - ema13    -- how far bears can drag price below value

The classic read: in an uptrend (EMA rising), watch bear_power. As long
as it stays below zero but starts RISING (bears losing grip on the dip),
that is Elder's long trigger -- "buy value in an uptrend when the bears
are weakening". Mirror for shorts in a downtrend.

Columns:

    ema13        -- EMA(close, 13)
    ema13_slope  -- +1 when ema13 rising, -1 falling, 0 flat (float, NaN in warmup)
    bull_power   -- h - ema13
    bear_power   -- l - ema13
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: EMA with min_periods=13, everything else is arithmetic on
the bar's own data. Warmup bars carry NaN for ema13 (and hence the powers);
signals.py fills those to False.
"""

import pandas as pd

from strategies import base as B

EMA_N = 13  # Elder's fixed constant (fixed a priori, no tuning)
ATR_N = 14


def add_indicators(df: pd.DataFrame, n: int = EMA_N) -> pd.DataFrame:
    df = df.copy()
    ema13 = B.ema(df["c"], n)
    df["ema13"] = ema13
    slope = ema13.diff()
    # +1 rising / -1 falling / 0 flat, NaN wherever ema13 is NaN
    df["ema13_slope"] = slope.apply(
        lambda x: 1.0 if x > 0 else (-1.0 if x < 0 else 0.0)
    )
    df.loc[ema13.isna(), "ema13_slope"] = float("nan")
    df["bull_power"] = df["h"] - ema13
    df["bear_power"] = df["l"] - ema13
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
