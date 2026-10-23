"""Bullish/bearish engulfing two-candle reversal pattern + EMA(20) trend filter.

A bullish engulfing forms when a green (close > open) candle's *body*
fully covers the prior red (close < open) candle's body:

    bullish_eng = (c > o) & (c.shift(1) < o.shift(1)) \
                & (c >= o.shift(1)) & (o <= c.shift(1))

The current body's range [open, close] must span the entire prior
body's range [close, open]. Wicks are deliberately ignored: a candle
whose wicks engulf but whose body does not is NOT a valid signal —
that is an indecision bar, not a rejection bar. The bearish mirror
swaps o/c and the inequalities.

No lookahead: detection at bar j uses only bars j-1 and j, so the
signal is known at bar j's close. The canon demands acting on the
CLOSED engulfing candle (never intrabar) and trading it WITH the
higher-timeframe trend: dip-buy bullish engulfings only when the
close is above EMA(20), rally-sell bearish engulfings only when the
close is below EMA(20).

Columns:

    ema20        -- exponential moving average of close, span 20
    bullish_eng  -- boolean, two-candle bullish engulfing body cover
    bearish_eng  -- boolean, two-candle bearish engulfing body cover
    atr          -- Wilder ATR(14) for the risk layer
"""

import pandas as pd

from strategies import base as B

EMA_N = 20  # trend-filter length, fixed a priori


def bullish_engulfing(o: pd.Series, c: pd.Series) -> pd.Series:
    """True where the current green body fully covers the prior red body."""
    po, pc = o.shift(1), c.shift(1)
    return (
        (c > o)          # current bar is bullish
        & (pc < po)      # prior bar is bearish
        & (c >= po)      # current close at/above prior open
        & (o <= pc)      # current open at/below prior close
    ).fillna(False).astype(bool)


def bearish_engulfing(o: pd.Series, c: pd.Series) -> pd.Series:
    """True where the current red body fully covers the prior green body."""
    po, pc = o.shift(1), c.shift(1)
    return (
        (c < o)          # current bar is bearish
        & (pc > po)      # prior bar is bullish
        & (c <= po)      # current close at/below prior open
        & (o >= pc)      # current open at/above prior close
    ).fillna(False).astype(bool)


def add_indicators(df: pd.DataFrame, ema_n: int = EMA_N) -> pd.DataFrame:
    df = df.copy()
    df["ema20"] = B.ema(df["c"], ema_n)
    df["bullish_eng"] = bullish_engulfing(df["o"], df["c"])
    df["bearish_eng"] = bearish_engulfing(df["o"], df["c"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
