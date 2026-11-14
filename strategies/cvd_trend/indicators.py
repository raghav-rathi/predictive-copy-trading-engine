"""Cumulative Volume Delta (CVD) trend (order-flow, classic).

True CVD needs tick-level bid/ask classification: delta_t = volume
traded at the ask - volume traded at the bid, CVD = cumsum(delta).
Hyperliquid 1h candles carry no bid/ask split, so this engine uses
the standard close-location proxy (documented approximation):

    cl       = (c - l) / (h - l)          (0 at the low, 1 at the high)
    buy_vol  = v * cl
    sell_vol = v - buy_vol
    delta    = buy_vol - sell_vol = v * (2*cl - 1)
    cvd      = cumsum(delta)

A bar closing near its high is treated as mostly buyer-initiated, a
bar closing near its low as mostly seller-initiated. That is a
reasonable proxy on trending bars and a weak one on doji / wide-range
bars — see README. Columns:

    cvd        -- cumulative volume delta (close-location proxy)
    cvd_ema20  -- EMA(CVD, 20)
    cvd_slope  -- one-bar change of EMA(CVD, 20)
    ema50      -- EMA(close, 50) trend filter
    atr        -- Wilder ATR(14) for the risk layer

No lookahead: every column on bar j uses data through bar j only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CVD_EMA_N = 20
PRICE_EMA_N = 50


def volume_delta(o: pd.Series, h: pd.Series, l: pd.Series,
                 c: pd.Series, v: pd.Series) -> pd.Series:
    """Per-bar volume delta via the close-location proxy."""
    rng = (h - l).replace(0.0, np.nan)
    cl = ((c - l) / rng).fillna(0.5)  # flat bar: split volume 50/50
    cl = cl.clip(0.0, 1.0)
    return v * (2.0 * cl - 1.0)


def add_indicators(df: pd.DataFrame, cvd_n: int = CVD_EMA_N,
                   price_n: int = PRICE_EMA_N) -> pd.DataFrame:
    df = df.copy()
    delta = volume_delta(df["o"], df["h"], df["l"], df["c"], df["v"])
    df["cvd"] = delta.cumsum()
    df["cvd_ema20"] = B.ema(df["cvd"], cvd_n)
    df["cvd_slope"] = df["cvd_ema20"] - df["cvd_ema20"].shift(1)
    df["ema50"] = B.ema(df["c"], price_n)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
