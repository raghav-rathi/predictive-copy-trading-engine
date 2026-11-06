"""EMA Pullback signals: trend-following pullback continuation.

Long only when close is above EMA(50). A pullback touch is a bar whose low
falls in the band [EMA(20) - 1.0*ATR, EMA(20) + 0.5*ATR]; a long entry fires
when a touch occurred within the last 5 bars and the close is back above
EMA(20) and above the prior close. Short is the mirror image.

All comparisons of close/low/high against an indicator use the PRIOR bar's
indicator values (shifted by 1): EMA/ATR are computed from the current
bar's close, so comparing the current bar's price to its own EMA would be
lookahead.
"""

import pandas as pd

TOUCH_WINDOW = 5


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ema20 = df["ema20"].shift(1)
    ema50 = df["ema50"].shift(1)
    atr = df["atr14"].shift(1)

    touch_long = (df["l"] <= ema20 + 0.5 * atr) & (df["l"] >= ema20 - 1.0 * atr)
    touch_short = (df["h"] >= ema20 - 0.5 * atr) & (df["h"] <= ema20 + 1.0 * atr)
    touch_long_recent = touch_long.rolling(TOUCH_WINDOW, min_periods=1).max() > 0
    touch_short_recent = touch_short.rolling(TOUCH_WINDOW, min_periods=1).max() > 0

    prev_c = df["c"].shift(1)
    df["long_entry"] = (
        (df["c"] > ema50) & touch_long_recent & (df["c"] > ema20) & (df["c"] > prev_c)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (df["c"] < ema50) & touch_short_recent & (df["c"] < ema20) & (df["c"] < prev_c)
    ).fillna(False).astype(bool)
    df["long_exit"] = (df["c"] < ema20).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > ema20).fillna(False).astype(bool)
    return df
