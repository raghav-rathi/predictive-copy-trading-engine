"""Relative Vigor Index indicators (John Ehlers).

Premise: prices tend to close above the open in uptrends and below the
open in downtrends, relative to the bar's range. The (1,2,2,1) weights
smooth both the numerator (close-open) and denominator (high-low) over
four bars, the ratio is smoothed over 10 bars, and the signal line is
the same (1,2,2,1) weighting applied to the RVI itself.

Columns:
    rvi        -- SMA(10) of weighted (close-open) / SMA(10) of
                  weighted (high-low); zero when the range is zero
    rvi_signal -- (1,2,2,1)-weighted mean of the last four RVI values
    atr        -- Wilder ATR(14) for the risk layer

All windows use only bars up to and including the current bar, so
the indicators are strictly causal.
"""

import numpy as np
import pandas as pd

from strategies import base as B

SMOOTH = 10


def _weighted4(s: pd.Series) -> pd.Series:
    """(1,2,2,1)/6 weighting over the current and prior three bars."""
    w = np.array([1.0, 2.0, 2.0, 1.0])
    return (
        s + 2 * s.shift(1) + 2 * s.shift(2) + s.shift(3)
    ) / 6.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    num = _weighted4(df["c"] - df["o"])
    den = _weighted4(df["h"] - df["l"])
    rvi = B.sma(num, SMOOTH) / B.sma(den, SMOOTH).replace(0, np.nan)
    df["rvi"] = rvi.fillna(0.0)
    df["rvi_signal"] = _weighted4(df["rvi"])
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
