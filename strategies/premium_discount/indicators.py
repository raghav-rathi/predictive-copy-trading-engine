"""Premium/discount (ICT equilibrium) indicators.

Rolling 48-bar dealing range (Michael Huddleston / ICT):

    range_high = max(h, 48)
    range_low  = min(l, 48)
    eq         = (range_high + range_low) / 2   (equilibrium)
    premium    = range_low + 0.75 * (range_high - range_low)
    discount   = range_low + 0.25 * (range_high - range_low)

A "touch" records whether price visited the far side of the range
in the last 12 bars: the low touched discount (min low over the
last 12 bars <= discount level) or the high touched premium
(max high over the last 12 bars >= premium level). The trade is
a mean-reversion-into-trend setup: price sweeps one extreme of
the range, then reclaims equilibrium.

Columns:
    range_high, range_low -- 48-bar range extremes
    eq        -- equilibrium (midpoint of the range)
    premium   -- 75% retracement level of the range
    discount  -- 25% retracement level of the range
    low_touch -- lowest low of the last 12 bars
    high_touch-- highest high of the last 12 bars
    touched_discount -- low_touch <= discount
    touched_premium  -- high_touch >= premium

No lookahead: every value on bar j uses data through bar j's
close only (rolling windows with min_periods=n, all inclusive
of bar j).
"""

import pandas as pd

LOOKBACK = 48    # shipped default
TOUCH_BARS = 12  # bars over which a discount/premium touch is remembered


def add_indicators(
    df: pd.DataFrame,
    lookback: int = LOOKBACK,
    touch_bars: int = TOUCH_BARS,
) -> pd.DataFrame:
    df = df.copy()
    df["range_high"] = df["h"].rolling(lookback, min_periods=lookback).max()
    df["range_low"] = df["l"].rolling(lookback, min_periods=lookback).min()
    rng = df["range_high"] - df["range_low"]
    df["eq"] = (df["range_high"] + df["range_low"]) / 2.0
    df["premium"] = df["range_low"] + 0.75 * rng
    df["discount"] = df["range_low"] + 0.25 * rng
    df["low_touch"] = df["l"].rolling(touch_bars, min_periods=touch_bars).min()
    df["high_touch"] = df["h"].rolling(touch_bars, min_periods=touch_bars).max()
    df["touched_discount"] = df["low_touch"] <= df["discount"]
    df["touched_premium"] = df["high_touch"] >= df["premium"]
    return df
