"""Belt Hold signals (Steve Nison).

Bullish belt hold: downtrend context, then a tall white candle that opens
within 10% of its range of the low, body >= 60% of the range, with little or
no upper shadow. Bearish belt hold is the mirror image in an uptrend.

Trend context uses only prior bars (shifted by 1): close below EMA(20) on
at least 3 of the last 5 prior bars, or a 5-bar return below -1% (bullish
context); the mirror for bearish context. The candle shape itself is the
signal bar's own OHLC, which is known at that bar's close.
Zero-range bars can never qualify (range guard via body_frac NaN -> False).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    ema20 = df["ema20"]

    below_ema = (c < ema20).shift(1)
    above_ema = (c > ema20).shift(1)
    ret5 = (c / c.shift(5) - 1).shift(1)

    downtrend = (below_ema.rolling(5, min_periods=5).sum() >= 3) | (ret5 < -0.01)
    uptrend = (above_ema.rolling(5, min_periods=5).sum() >= 3) | (ret5 > 0.01)

    rng = df["candle_range"]
    white = df["c"] > df["o"]
    black = df["c"] < df["o"]

    bullish = (
        downtrend
        & white
        & (df["open_low_frac"] <= 0.10)
        & (df["body_frac"] >= 0.60)
        & (df["upper_shadow_frac"] <= 0.15)
    )
    bearish = (
        uptrend
        & black
        & (df["open_high_frac"] <= 0.10)
        & (df["body_frac"] >= 0.60)
        & (df["lower_shadow_frac"] <= 0.15)
    )
    df["long_entry"] = bullish.fillna(False).astype(bool)
    df["short_entry"] = bearish.fillna(False).astype(bool)
    # Exit on the opposite belt hold appearing.
    df["long_exit"] = bearish.fillna(False).astype(bool)
    df["short_exit"] = bullish.fillna(False).astype(bool)
    return df
