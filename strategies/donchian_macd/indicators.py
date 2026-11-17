"""Donchian(20) channel + MACD(12,26,9) confirmation indicators.

Long: close breaks above the trailing 20-bar high AND MACD
histogram > 0.
Short: close breaks below the trailing 20-bar low AND MACD
histogram < 0.

The Donchian high/low are the extremes of the PREVIOUS 20 bars
(shifted by 1): a close can only "break above" a high that does
not already include the current bar's high (which is always >=
the close). See CALIBRATION.md. MACD via strategies.base.macd.

Columns:
    donchian_high_20 -- max high of the previous 20 bars
    donchian_low_20  -- min low of the previous 20 bars
    macd             -- MACD line (EMA12 - EMA26)
    macd_signal      -- EMA9 of the MACD line
    macd_hist        -- macd - macd_signal
    atr              -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

DONCHIAN_N = 20
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

INDICATOR_COLS = ["donchian_high_20", "donchian_low_20", "macd",
                  "macd_signal", "macd_hist", "atr"]


def add_indicators(df: pd.DataFrame, n: int = DONCHIAN_N,
                   fast: int = MACD_FAST, slow: int = MACD_SLOW,
                   signal: int = MACD_SIGNAL) -> pd.DataFrame:
    df = df.copy()
    # Previous-20-bars extremes (shifted by 1) — see module docstring.
    df["donchian_high_20"] = df["h"].rolling(n, min_periods=n).max().shift(1)
    df["donchian_low_20"] = df["l"].rolling(n, min_periods=n).min().shift(1)
    m = B.macd(df["c"], fast, slow, signal)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
