"""Donchian channel + EMA filter indicators (Turtle System 1 style).

Donchian(20): upper = highest high of the PREVIOUS 20 bars, lower =
lowest low of the previous 20 bars (the current bar is excluded, so
a breakout is measured against a level known before the bar opens).
EMA(50) is the trend filter. Exits use the Turtle System 1 exit:
a long exits on a close below the lowest low of the previous 10
bars; a short exits on a close above the highest high of the
previous 10 bars.

Columns:
    donchian_upper -- highest high of the previous 20 bars
    donchian_lower -- lowest low of the previous 20 bars
    ema_50         -- EMA(50) of close
    exit_low_10    -- lowest low of the previous 10 bars
    exit_high_10   -- highest high of the previous 10 bars
    atr            -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close
only; the Donchian/exit levels on bar i use bars i-20..i-1 and
i-10..i-1 respectively (shifted by one).
"""

import pandas as pd

from strategies import base as B

DONCHIAN_N = 20
EMA_N = 50
EXIT_N = 10

INDICATOR_COLS = ["donchian_upper", "donchian_lower", "ema_50",
                  "exit_low_10", "exit_high_10", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["donchian_upper"] = (
        df["h"].rolling(DONCHIAN_N, min_periods=DONCHIAN_N).max().shift(1)
    )
    df["donchian_lower"] = (
        df["l"].rolling(DONCHIAN_N, min_periods=DONCHIAN_N).min().shift(1)
    )
    df["ema_50"] = B.ema(df["c"], EMA_N)
    df["exit_low_10"] = (
        df["l"].rolling(EXIT_N, min_periods=EXIT_N).min().shift(1)
    )
    df["exit_high_10"] = (
        df["h"].rolling(EXIT_N, min_periods=EXIT_N).max().shift(1)
    )
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
