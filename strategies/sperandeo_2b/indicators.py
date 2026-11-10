"""Sperandeo 2B pattern indicators.

Victor Sperandeo's 2B (false-breakout) reversal, from "Trader Vic II:
Principles of Professional Speculation" (John Wiley & Sons, 1994).

The 2B Top: price makes a new 20-bar high, pulls back for at least
3 bars without making a new 20-bar high, then a later bar closes
above that 20-bar high (the breakout bar), and a subsequent bar
closes below the breakout bar's low. That close is the 2B short
signal. The 2B Bottom is the exact mirror.

This module computes only the causal building blocks: the rolling
20-bar high/low and the new-extreme flags. The pattern state machine
lives in signals.py. Every value on bar i uses only data through
bar i's close.
"""

import pandas as pd

from strategies.base import atr

LOOKBACK = 20

INDICATOR_COLS = [
    "high20",
    "low20",
    "is_new_high",
    "is_new_low",
    "atr14",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    h = df["h"]
    l = df["l"]
    high20 = h.rolling(LOOKBACK, min_periods=LOOKBACK).max()
    low20 = l.rolling(LOOKBACK, min_periods=LOOKBACK).min()
    df["high20"] = high20
    df["low20"] = low20
    # A new 20-bar high is a bar whose high equals the rolling 20-bar
    # maximum (current bar included). Same for lows.
    df["is_new_high"] = (h == high20).fillna(False).astype(bool)
    df["is_new_low"] = (l == low20).fillna(False).astype(bool)
    df["atr14"] = atr(h, l, df["c"], 14)
    return df
