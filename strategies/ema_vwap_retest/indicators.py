"""EMA/VWAP breakout-retest indicators.

Source: @EllyDtrades "Copy and Paste Strategy" (X thread, Nov 2024, full
text verified via Thread Reader). Core system: 8 EMA, 20 EMA, session VWAP,
previous-day high/low levels. Breakout + retest/pullback entries, 8 EMA
trailing exits.

Crypto adaptation: no pre-market session exists (24/7 market), so PMH/PML
are dropped; PDH/PDL computed from 1h bars (24-bar rolling extremes).
"""

import pandas as pd

from strategies import base as B


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema8"] = B.ema(df["c"], 8)
    df["ema20"] = B.ema(df["c"], 20)
    df["vwap"] = B.anchored_vwap(df["h"], df["l"], df["c"], df["v"], df["t"])
    # previous-day high/low: 24-bar rolling extremes shifted by a full day
    df["pdh"] = df["h"].rolling(24, min_periods=24).max().shift(24)
    df["pdl"] = df["l"].rolling(24, min_periods=24).min().shift(24)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
