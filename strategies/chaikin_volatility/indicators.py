"""Chaikin Volatility (Marc Chaikin).

    ema_hl  = EMA(high - low, n)
    cv      = 100 * (ema_hl - ema_hl.shift(roc)) / ema_hl.shift(roc)
    sma50   = SMA(close, ma)      -- directional filter

The Chaikin Volatility oscillator measures the rate of change of the
EMA of the high-low trading range: cv > 0 means the average range is
*expanding* (volatility rising), cv < 0 means it is contracting. It is
deliberately direction-agnostic — a range-expansion spike fires the
same way on an up day as on a down day. Chaikin's own observation was
that sharp volatility spikes tend to precede price reversals, because
a surge in range expansion marks climactic, emotional participation;
the directional filter (SMA50) here trades *with* the prevailing trend
into the expansion rather than fading it.

Columns:

    cv    -- Chaikin Volatility(n, roc)
    ema_hl -- the EMA of the high-low range itself
    sma50 -- SMA(close, 50) trend filter
    atr   -- Wilder ATR(14) for the risk layer

No lookahead: EMA (min_periods=n) and sma (min_periods=ma) use data
through bar j only; cv's first valid value arrives after ~n + roc
bars, well inside WARMUP=70.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CV_N = 10       # shipped default: EMA length of the high-low range
CV_ROC = 10     # shipped default: ROC lookback of the range EMA
MA_LEN = 50     # shipped default: SMA trend filter length


def chaikin_vol(df: pd.DataFrame, n: int = CV_N,
                roc: int = CV_ROC) -> pd.DataFrame:
    """Chaikin Volatility oscillator from high/low series."""
    ema_hl = B.ema(df["h"] - df["l"], n)
    prev = ema_hl.shift(roc)
    cv = 100.0 * (ema_hl - prev) / prev.replace(0.0, np.nan)
    return pd.DataFrame({"ema_hl": ema_hl, "cv": cv})


def add_indicators(df: pd.DataFrame, n: int = CV_N,
                   roc: int = CV_ROC, ma: int = MA_LEN) -> pd.DataFrame:
    df = df.copy()
    t = chaikin_vol(df, n, roc)
    df["ema_hl"] = t["ema_hl"]
    df["cv"] = t["cv"]
    df["sma50"] = B.sma(df["c"], ma)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
