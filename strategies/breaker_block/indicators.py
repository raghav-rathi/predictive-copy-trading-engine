"""Breaker block indicators (ICT Smart Money Concepts, M. J. Huddleston).

An ORDER BLOCK is the last opposing closed bar before an impulsive
move that breaks structure:

    bullish OB = the last down-closed bar before a close above the
                 prior 20-bar high; the zone is that bar's [low, high]
    bearish OB = the last up-closed bar before a close below the
                 prior 20-bar low; the zone is that bar's [low, high]

The most recent OB per direction is kept; a newer OB of the same
direction replaces the older one. An OB is cleared (columns go NaN)
on the bar price closes through it — through the low for a bullish
OB, through the high for a bearish OB — which is where the breaker
forms (see signals.py).

Columns:

    prev20_high, prev20_low -- prior 20-bar extremes (excluding
                               the current bar)
    down_closed, up_closed  -- close < open / close > open
    ob_bull_high, ob_bull_low, ob_bull_bar -- active bullish OB
    ob_bear_high, ob_bear_low, ob_bear_bar -- active bearish OB
    atr (Wilder ATR(14) for the risk layer)

No lookahead: every value on bar i uses data through bar i's close.
The 20-bar lookback and the 10-bar search window for the last
opposing bar are fixed a priori (see CALIBRATION.md).
"""

import numpy as np
import pandas as pd

from strategies import base as B

STRUCTURE_N = 20
OB_SEARCH_N = 10

INDICATOR_COLS = ["prev20_high", "prev20_low", "down_closed",
                  "up_closed", "ob_bull_high", "ob_bull_low",
                  "ob_bull_bar", "ob_bear_high", "ob_bear_low",
                  "ob_bear_bar", "atr"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    h = df["h"].to_numpy()
    l = df["l"].to_numpy()
    o = df["o"].to_numpy()
    c = df["c"].to_numpy()
    prev20_high = df["h"].shift(1).rolling(STRUCTURE_N,
                                           min_periods=STRUCTURE_N).max()
    prev20_low = df["l"].shift(1).rolling(STRUCTURE_N,
                                          min_periods=STRUCTURE_N).min()
    down_closed = df["c"] < df["o"]
    up_closed = df["c"] > df["o"]

    bull_high = np.full(n, np.nan)
    bull_low = np.full(n, np.nan)
    bull_bar = np.full(n, -1)
    bear_high = np.full(n, np.nan)
    bear_low = np.full(n, np.nan)
    bear_bar = np.full(n, -1)

    cur_bull = None  # (high, low, bar)
    cur_bear = None
    for i in range(n):
        # Impulsive break of structure -> (re)define the order block
        # as the last opposing closed bar within the search window.
        if not np.isnan(prev20_high.iloc[i]) and c[i] > prev20_high.iloc[i]:
            for j in range(i - 1, max(-1, i - 1 - OB_SEARCH_N), -1):
                if c[j] < o[j]:
                    cur_bull = (h[j], l[j], j)
                    break
        if not np.isnan(prev20_low.iloc[i]) and c[i] < prev20_low.iloc[i]:
            for j in range(i - 1, max(-1, i - 1 - OB_SEARCH_N), -1):
                if c[j] > o[j]:
                    cur_bear = (h[j], l[j], j)
                    break
        # Close through the block invalidates it as an order block;
        # the breaker forms in signals.py from the cleared zone.
        if cur_bull is not None and c[i] < cur_bull[1]:
            cur_bull = None
        if cur_bear is not None and c[i] > cur_bear[0]:
            cur_bear = None
        if cur_bull is not None:
            bull_high[i], bull_low[i], bull_bar[i] = cur_bull
        if cur_bear is not None:
            bear_high[i], bear_low[i], bear_bar[i] = cur_bear

    df["prev20_high"] = prev20_high
    df["prev20_low"] = prev20_low
    df["down_closed"] = down_closed.fillna(False).astype(bool)
    df["up_closed"] = up_closed.fillna(False).astype(bool)
    df["ob_bull_high"] = bull_high
    df["ob_bull_low"] = bull_low
    df["ob_bull_bar"] = bull_bar
    df["ob_bear_high"] = bear_high
    df["ob_bear_low"] = bear_low
    df["ob_bear_bar"] = bear_bar
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
