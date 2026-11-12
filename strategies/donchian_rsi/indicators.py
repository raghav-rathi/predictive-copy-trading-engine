"""Donchian + RSI indicators.

Richard Donchian's channel (1970s, the core of the Turtle system):
the 20-bar high and low, computed over the PRIOR 20 bars excluding
the current bar, so a close above the channel high is a genuine
breakout rather than a self-referential one. RSI(14) (Wilder)
confirms the breakout has momentum behind it.

    don_high20 -- max high of the prior 20 bars (excluding bar i)
    don_low20  -- min low of the prior 20 bars (excluding bar i)
    rsi        -- Wilder RSI(14)
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every column on bar i uses only data through bar i's
close (the Donchian levels use bars i-20..i-1).
"""

import pandas as pd

from strategies import base as B

DONCHIAN_N = 20
RSI_N = 14

INDICATOR_COLS = ["don_high20", "don_low20", "rsi", "atr"]


def add_indicators(df: pd.DataFrame, n: int = DONCHIAN_N,
                   rsi_n: int = RSI_N) -> pd.DataFrame:
    df = df.copy()
    # Shift first: the channel is the prior n bars' extremes, the
    # current bar excluded. B.donchian on the shifted series gives
    # max(h[i-n..i-1]) / min(l[i-n..i-1]).
    ch = B.donchian(df["h"].shift(1), df["l"].shift(1), n)
    df["don_high20"] = ch[f"donchian_high_{n}"]
    df["don_low20"] = ch[f"donchian_low_{n}"]
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
