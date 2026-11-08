"""Three white soldiers / three black crows indicators.

tws_bullish is True on the bar where the third white soldier
completes: three consecutive bullish candles, each closing above the
previous close, opening inside the previous candle's body, with an
upper wick no more than 25% of its range and a body at least 0.5 x
ATR(14). tws_bearish is the mirror (three black crows). sma50 is the
50-bar simple moving average of close; atr14 is Wilder ATR(14). All
quantities use only data through bar i's close.
"""

import numpy as np
import pandas as pd

from strategies.base import atr, sma

SMA_BARS = 50
ATR_BARS = 14
TREND_BARS = 5
MAX_WICK_FRAC = 0.25
MIN_BODY_ATR = 0.5

INDICATOR_COLS = [
    "tws_sma50",
    "tws_atr14",
    "tws_bullish",
    "tws_bearish",
]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    o = df["o"]
    h = df["h"]
    l = df["l"]
    c = df["c"]
    df["tws_sma50"] = sma(c, SMA_BARS)
    df["tws_atr14"] = atr(h, l, c, ATR_BARS)
    a = df["tws_atr14"]
    rng = h - l
    prev_o = o.shift(1)
    prev_c = c.shift(1)
    body_lo = np.minimum(prev_o, prev_c)
    body_hi = np.maximum(prev_o, prev_c)
    open_inside = (o > body_lo) & (o < body_hi)
    # Bullish candle: up close, higher close, open inside prev body,
    # small upper wick, body >= 0.5 x ATR.
    bull_candle = (
        (c > o)
        & (c > prev_c)
        & open_inside
        & ((h - np.maximum(o, c)) <= MAX_WICK_FRAC * rng)
        & ((c - o) >= MIN_BODY_ATR * a)
    ).fillna(False)
    # Bearish candle: mirror with the lower wick.
    bear_candle = (
        (c < o)
        & (c < prev_c)
        & open_inside
        & ((np.minimum(o, c) - l) <= MAX_WICK_FRAC * rng)
        & ((o - c) >= MIN_BODY_ATR * a)
    ).fillna(False)
    # Three consecutive qualifying candles ending on bar i.
    bull3 = bull_candle & bull_candle.shift(1).fillna(False) & bull_candle.shift(2).fillna(False)
    bear3 = bear_candle & bear_candle.shift(1).fillna(False) & bear_candle.shift(2).fillna(False)
    # Trend over the 5 bars before the 3-bar pattern (bars i-7..i-3).
    down_trend = ((c < df["tws_sma50"]).rolling(TREND_BARS, min_periods=TREND_BARS).sum() == TREND_BARS).shift(3)
    up_trend = ((c > df["tws_sma50"]).rolling(TREND_BARS, min_periods=TREND_BARS).sum() == TREND_BARS).shift(3)
    df["tws_bullish"] = (bull3 & down_trend.fillna(False)).astype(bool)
    df["tws_bearish"] = (bear3 & up_trend.fillna(False)).astype(bool)
    return df
