"""Donald Lambert CCI(20) mean-reversion indicators (StockCharts).

The Commodity Channel Index measures how far the typical price
has strayed from its own moving average, in units of mean
deviation:

    tp   = (h + l + c) / 3
    sma  = SMA(tp, 20)
    md   = mean(|tp - sma|) over the same 20 bars (the current
           window's mean applied to every bar in the window,
           the canonical TA-Lib definition)
    cci  = (tp - sma) / (0.015 * md)

The 0.015 constant scales CCI so that ~70-80% of readings fall
inside +/-100 in Lambert's original design. A reading beyond
+100 means price is stretched far above its average; below -100
means stretched far below. The strategy trades the *cross back
through* the level, not the level itself.

Columns:

    cci -- CCI(20), 0 when the 20-bar mean deviation is zero
    atr -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n). A zero
mean deviation (a dead-flat window) maps to CCI = 0, the neutral
midpoint, instead of dividing by zero.
"""

import numpy as np
import pandas as pd

from strategies import base as B

CCI_N = 20         # shipped default (fixed a priori, Lambert's standard)
LONG_LEVEL = -100  # long trigger: cross above from below
SHORT_LEVEL = 100  # short trigger: cross below from above
SCALE = 0.015      # Lambert's scaling constant


def _mean_dev(window: np.ndarray) -> float:
    return float(np.mean(np.abs(window - window.mean())))


def add_indicators(df: pd.DataFrame, cci_n: int = CCI_N) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    sma = tp.rolling(cci_n, min_periods=cci_n).mean()
    md = tp.rolling(cci_n, min_periods=cci_n).apply(_mean_dev, raw=True)
    cci = (tp - sma) / (SCALE * md)
    cci = cci.where(md != 0, 0.0)
    df["cci"] = cci.ffill().bfill()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
