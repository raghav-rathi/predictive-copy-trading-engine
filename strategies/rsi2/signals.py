"""RSI(2) mean-reversion signals.

Long  when c > SMA200 and RSI(2) < 10   (deep pullback in uptrend)
Short when c < SMA200 and RSI(2) > 90   (deep rip in downtrend)
Exit long  when c > SMA5 or RSI(2) > 85  (snap-back complete)
Exit short when c < SMA5 or RSI(2) < 15
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["sma200"].notna() & df["rsi2"].notna()  # no trades during warmup
    uptrend = df["c"] > df["sma200"]
    df["long_entry"] = uptrend & (df["rsi2"] < 10.0) & valid
    df["short_entry"] = (~uptrend) & (df["rsi2"] > 90.0) & valid
    df["long_exit"] = (df["c"] > df["sma5"]) | (df["rsi2"] > 85.0)
    df["short_exit"] = (df["c"] < df["sma5"]) | (df["rsi2"] < 15.0)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
