"""Marc Chaikin Accumulation/Distribution Line (ADL) indicators.

Money flow multiplier (Chaikin):

    mfm[j] = ((c[j] - l[j]) - (h[j] - c[j])) / (h[j] - l[j])

i.e. where the close sits inside the bar's range, scaled to [-1, 1]:
+1 when the close is on the high, -1 when on the low. The h == l
guard maps a zero-range bar to 0 (no range, no money-flow signal)
instead of dividing by zero.

    mfv[j] = mfm[j] * v[j]          (money flow volume)
    adl[j] = sum(mfv[0..j])         (cumulative accumulation/distribution)

The signal line is a plain 10-bar simple moving average of the ADL,
and the trend filter is a 50-bar SMA of close. All windows are
trailing (min_periods=n); no lookahead.

Columns:

    adl     -- cumulative money flow volume
    adl_sma -- SMA(adl, 10)
    sma50   -- SMA(close, 50)
    atr     -- Wilder ATR(14) for the risk layer
"""

import numpy as np
import pandas as pd

from strategies import base as B

ADL_SMA_N = 10  # signal-line length (fixed a priori)
SMA_N = 50      # trend-filter length (fixed a priori)


def money_flow_multiplier(h: pd.Series, l: pd.Series,
                          c: pd.Series) -> pd.Series:
    """Chaikin money flow multiplier in [-1, 1]; 0 on zero-range bars."""
    rng = h - l
    mfm = ((c - l) - (h - c)) / rng
    mfm = mfm.where(rng != 0, 0.0)
    return mfm.rename("mfm")


def accumulation_distribution_line(h: pd.Series, l: pd.Series,
                                   c: pd.Series, v: pd.Series) -> pd.Series:
    """Cumulative money flow volume (the ADL)."""
    mfv = (money_flow_multiplier(h, l, c) * v).to_numpy(dtype=float)
    return pd.Series(np.cumsum(mfv), index=h.index, name="adl")


def add_indicators(df: pd.DataFrame, adl_sma_n: int = ADL_SMA_N,
                   sma_n: int = SMA_N) -> pd.DataFrame:
    df = df.copy()
    df["adl"] = accumulation_distribution_line(df["h"], df["l"],
                                               df["c"], df["v"])
    df["adl_sma"] = (
        df["adl"].rolling(adl_sma_n, min_periods=adl_sma_n).mean()
    ).ffill().bfill()
    df["sma50"] = (
        df["c"].rolling(sma_n, min_periods=sma_n).mean()
    ).ffill().bfill()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
