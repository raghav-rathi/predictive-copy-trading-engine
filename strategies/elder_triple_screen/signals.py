"""Triple Screen signals (Alexander Elder, "Trading for a Living").

Screen 1 (the 6h MACD-histogram trend) is the tide: trade only with it.
Screen 2 (the 1h Force Index EMA(2)) is the wave: enter on a pullback
against the tide -- buy when the wave dips below zero in an uptrend,
sell short when it pops above zero in a downtrend.
(Screen 3's intraday stop-entry precision is approximated by the
harness's next-bar-open execution.)

long_entry  = trend_up_6h & force index crossed back below 0
short_entry = trend_down_6h & force index crossed back above 0
long_exit   = trend screen flipped (not trend_up_6h) -- Elder's exit rule
short_exit  = not trend_down_6h
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fi2 = df["fi_ema2"]
    zero = pd.Series(0.0, index=df.index)
    crossed_below_zero = (fi2 < zero) & (fi2.shift(1) >= zero)
    crossed_above_zero = (fi2 > zero) & (fi2.shift(1) <= zero)

    df["long_entry"] = (df["trend_up_6h"] & crossed_below_zero).fillna(False)
    df["short_entry"] = (df["trend_down_6h"] & crossed_above_zero).fillna(False)
    # Elder's exit: once the trend screen flips against you, the trade is
    # over -- the tide turned, not the wave.
    df["long_exit"] = (~df["trend_up_6h"]).fillna(False)
    df["short_exit"] = (~df["trend_down_6h"]).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
