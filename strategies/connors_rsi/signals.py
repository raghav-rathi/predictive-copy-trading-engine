"""Connors RSI(2) pullback signals (Larry Connors, R3 system).

Long entry: close > SMA(200) AND RSI(2) < 10 AND RSI(2) has declined
3 consecutive bars ending on the entry bar. Entry is the pullback bar
itself (executed next-bar open by the harness).
Long exit: RSI(2) > 70 OR close < SMA(50).

Short entry/exit are the exact mirror: close < SMA(200) AND RSI(2) > 90
AND RSI(2) rose 3 consecutive bars; exit on RSI(2) < 30 OR close > SMA(50).

Risk-level exits (2.5xATR stop, 30-bar max hold) come from risk.py.
"""

import pandas as pd

LONG_THRESH = 10.0
SHORT_THRESH = 90.0
LONG_EXIT_RSI = 70.0
SHORT_EXIT_RSI = 30.0

SIGNAL_COLS = ("long_entry", "short_entry", "long_exit", "short_exit")


def add_signals(
    df: pd.DataFrame,
    long_thresh: float = LONG_THRESH,
    short_thresh: float = SHORT_THRESH,
    long_exit_rsi: float = LONG_EXIT_RSI,
    short_exit_rsi: float = SHORT_EXIT_RSI,
) -> pd.DataFrame:
    df = df.copy()
    above_trend = df["c"] > df["sma200"]
    below_trend = df["c"] < df["sma200"]
    df["long_entry"] = (
        above_trend & (df["rsi2"] < long_thresh) & df["decl3"]
    ).fillna(False)
    df["long_exit"] = (
        (df["rsi2"] > long_exit_rsi) | (df["c"] < df["sma50"])
    ).fillna(False)
    df["short_entry"] = (
        below_trend & (df["rsi2"] > short_thresh) & df["rise3"]
    ).fillna(False)
    df["short_exit"] = (
        (df["rsi2"] < short_exit_rsi) | (df["c"] > df["sma50"])
    ).fillna(False)
    for col in SIGNAL_COLS:
        df[col] = df[col].fillna(False).astype(bool)
    return df
