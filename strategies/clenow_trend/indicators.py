"""Andreas Clenow trend-following indicators ("Following the Trend").

Day-scale parameters expressed in 1h bars (1 day = 24 bars):

  * Trend filter: EMA(1200) vs EMA(2400) of close — the 50-day and
    100-day EMAs. Bullish when the fast EMA is above the slow EMA.
  * Breakout levels: Donchian 1200-bar high / low (50-day extremes)
    of high / low.

All computation is causal: every value on bar i uses only data through
bar i's close. No forward-shifted series anywhere.
"""

import pandas as pd

from strategies.base import ema

EMA_FAST = 1200   # 50 days * 24 bars/day
EMA_SLOW = 2400   # 100 days * 24 bars/day
BREAKOUT_WINDOW = 1200  # 50 days * 24 bars/day

INDICATOR_COLS = [
    "ema_fast_1200",
    "ema_slow_2400",
    "donchian_high_1200",
    "donchian_low_1200",
    "bullish",
    "bearish",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    df["ema_fast_1200"] = ema(c, EMA_FAST)
    df["ema_slow_2400"] = ema(c, EMA_SLOW)
    # Rolling extremes include the current bar, so a close that equals
    # the rolling high is a new 1200-bar high on that very bar.
    df["donchian_high_1200"] = df["h"].rolling(BREAKOUT_WINDOW, min_periods=BREAKOUT_WINDOW).max()
    df["donchian_low_1200"] = df["l"].rolling(BREAKOUT_WINDOW, min_periods=BREAKOUT_WINDOW).min()
    df["bullish"] = (df["ema_fast_1200"] > df["ema_slow_2400"]).fillna(False).astype(bool)
    # Strictly two-sided: equal EMAs (e.g. flat price) are neither
    # bullish nor bearish, so no entry fires on a flat market.
    df["bearish"] = (df["ema_fast_1200"] < df["ema_slow_2400"]).fillna(False).astype(bool)
    return df
