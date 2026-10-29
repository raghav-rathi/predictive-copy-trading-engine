"""CCI(20) zero-line trend-cross indicators (Lambert CCI).

CCI = (typical price - SMA20(typical price)) / (0.015 * mean
deviation over 20 bars), Donald Lambert's construction, computed
exactly as in cci_extreme (rolling mean deviation around the
window's own mean, the canonical TA-Lib definition). This
strategy is NOT divergence (cci_divergence) and NOT the +/-100
extreme mean-reversion (cci_extreme): it trades the zero line
itself, the boundary between the oscillator's bearish and
bullish halves, and only in the direction of the price trend.

Columns:
    cci       -- CCI(20), 0 when the 20-bar mean deviation is zero
    trend_sma -- SMA(50) of close, the trend filter
    atr       -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n). A zero
mean deviation (a dead-flat window) maps to CCI = 0, the neutral
midpoint, instead of dividing by zero.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CCI_N = 20
TREND_N = 50
SCALE = 0.015


def _mean_dev(window: np.ndarray) -> float:
    return float(np.mean(np.abs(window - window.mean())))


def add_indicators(df: pd.DataFrame, cci_n: int = CCI_N) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    sma = tp.rolling(cci_n, min_periods=cci_n).mean()
    md = tp.rolling(cci_n, min_periods=cci_n).apply(_mean_dev, raw=True)
    cci = (tp - sma) / (SCALE * md)
    cci = cci.where(md != 0, 0.0)
    df["cci"] = cci
    df["trend_sma"] = B.sma(df["c"], TREND_N)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
