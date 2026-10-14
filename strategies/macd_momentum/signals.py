"""MACD momentum signals.

Long  when MACD hist crosses above 0 and close > EMA200
Short when MACD hist crosses below 0 and close < EMA200
Exit long  when hist crosses below 0; exit short when hist crosses above 0.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = (df["macd_hist"] > 0) & (df["macd_hist_prev"] <= 0)
    cross_dn = (df["macd_hist"] < 0) & (df["macd_hist_prev"] >= 0)
    valid = df["ema200"].notna()  # no trades during indicator warmup
    uptrend = df["c"] > df["ema200"]
    df["long_entry"] = cross_up & uptrend & valid
    df["short_entry"] = cross_dn & (~uptrend) & valid
    df["long_exit"] = cross_dn
    df["short_exit"] = cross_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
