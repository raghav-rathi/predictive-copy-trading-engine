"""Fibonacci pullback signals.

Long (uptrend: close > SMA200): the bar's low dips to/below the 50%
retracement of the trailing 60-bar swing high/low leg, holds above the
78.6% level, and the bar closes back above 61.8% -- a pullback reclaim.

Short (downtrend: close < SMA200): mirror on the 38.2-50% bounce zone
of the down leg -- high pushes into [sretr382, sretr50], holds below
61.8%, closes back below 38.2%.

Exits: long when close reaches the prior swing high (target achieved);
short when close reaches the prior swing low. The 78.6% invalidation
beyond the pocket is approximated by the 2xATR hard stop in risk.py
(the harness cannot place a level-based stop).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, l, h = df["c"], df["l"], df["h"]
    uptrend = c > df["sma200"]
    downtrend = c < df["sma200"]
    df["long_entry"] = (
        uptrend
        & (l <= df["lretr50"])
        & (l > df["lretr786"])
        & (c > df["lretr618"])
    ).fillna(False)
    df["short_entry"] = (
        downtrend
        & (h >= df["sretr382"])
        & (h < df["sretr618"])
        & (c < df["sretr382"])
    ).fillna(False)
    df["long_exit"] = (c >= df["swingH"]).fillna(False)
    df["short_exit"] = (c <= df["swingL"]).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
