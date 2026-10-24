"""George Lane Slow Stochastic indicators (StockCharts).

The fast stochastic measures where the close sits inside the
last N bars' range; the slow version smooths it, which is what
Lane himself traded:

    %K = 100 * (c - lowest_low_14) / (highest_high_14 - lowest_low_14)
    %D = SMA(3) of %K

%K is the raw position-in-range (0 = at the 14-bar low, 100 = at
the 14-bar high); %D is its 3-bar simple average and is the
signal line. Readings below 20 mark an oversold range, above 80
an overbought one — but the strategy never trades the level
alone, only the %K/%D cross inside the extreme zone.

Columns:

    stoch_k -- %K, 0..100 (50 when the 14-bar range is zero)
    stoch_d -- %D, SMA(3) of %K
    atr     -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n). A zero
14-bar range (a dead-flat window) maps to %K = 50, the neutral
midpoint, instead of dividing by zero.
"""

import numpy as np
import pandas as pd

from strategies import base as B

K_N = 14          # shipped default (fixed a priori, Lane's standard)
D_N = 3           # %D smoothing (the "slow" in Slow Stochastic)
OVERSOLD = 20     # oversold zone boundary
OVERBOUGHT = 80   # overbought zone boundary


def add_indicators(df: pd.DataFrame, k_n: int = K_N,
                   d_n: int = D_N) -> pd.DataFrame:
    df = df.copy()
    ll = df["l"].rolling(k_n, min_periods=k_n).min()
    hh = df["h"].rolling(k_n, min_periods=k_n).max()
    rng = hh - ll
    pct_k = (100.0 * (df["c"] - ll) / rng).where(rng != 0, 50.0)
    df["stoch_k"] = pct_k.ffill().bfill()
    pct_d = pct_k.rolling(d_n, min_periods=d_n).mean()
    df["stoch_d"] = pct_d.ffill().bfill()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
