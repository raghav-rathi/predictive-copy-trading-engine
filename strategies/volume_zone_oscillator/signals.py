"""Volume Zone Oscillator signals (Khalil's published system).

Long entry (uptrend context only: close > EMA(60) and ADX(14) > 18):
  * VZO crosses above -40 (oversold reversal), OR
  * VZO crosses above 0 while the lowest VZO in the last 10 bars stayed
    above -40 (failed pullback that never reached oversold).
Short entry (downtrend context only: close < EMA(60) and ADX(14) > 18):
  * VZO crosses below +40 (overbought reversal), OR
  * VZO crosses below 0 while the highest VZO in the last 10 bars stayed
    below +40.

Exits:
  * long_exit on VZO crossing below 0 OR close crossing below EMA(60).
  * short_exit on VZO crossing above 0 OR close crossing above EMA(60).

All inputs are computed from data through bar i's close, so signals on
bar i use no future data. The "last 10 bars" window is the trailing
10-bar window ending on bar i (inclusive).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.volume_zone_oscillator.indicators import (
    ADX_MIN,
    VZO_OVERBOUGHT,
    VZO_OVERSOLD,
)

LOOKBACK_BARS = 10


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    vzo = df["vzo"]
    ema60 = df["ema60"]
    adx_v = df["adx"]
    c = df["c"]

    uptrend = (c > ema60) & (adx_v > ADX_MIN)
    downtrend = (c < ema60) & (adx_v > ADX_MIN)

    cross_up_oversold = crossed_above(vzo, VZO_OVERSOLD)
    cross_up_zero = crossed_above(vzo, 0.0)
    cross_down_overbought = crossed_below(vzo, VZO_OVERBOUGHT)
    cross_down_zero = crossed_below(vzo, 0.0)

    # Lowest / highest VZO over the trailing 10-bar window ending on bar i.
    vzo_min_10 = vzo.rolling(LOOKBACK_BARS, min_periods=LOOKBACK_BARS).min()
    vzo_max_10 = vzo.rolling(LOOKBACK_BARS, min_periods=LOOKBACK_BARS).max()
    never_oversold = vzo_min_10 > VZO_OVERSOLD
    never_overbought = vzo_max_10 < VZO_OVERBOUGHT

    long_entry = uptrend & (
        cross_up_oversold | (cross_up_zero & never_oversold)
    )
    short_entry = downtrend & (
        cross_down_overbought | (cross_down_zero & never_overbought)
    )

    long_exit = crossed_below(vzo, 0.0) | crossed_below(c, ema60)
    short_exit = crossed_above(vzo, 0.0) | crossed_above(c, ema60)

    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
