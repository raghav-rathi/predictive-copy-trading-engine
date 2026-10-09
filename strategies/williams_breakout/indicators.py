"""Larry Williams volatility-breakout indicators.

Classic Williams breakout: buy when price exceeds the prior bar's high by a
fraction of its range — volatility expansion confirms commitment. Here on
1h bars: enter long when close > prior 24h high AND the 24h range is
expanded (> 1.5x its 20-bar average); mirror for shorts. The expansion
filter keeps it from buying every marginal new high in dead markets.
"""

import pandas as pd

from strategies import base as B

LOOKBACK = 24
RANGE_MULT = 1.5
RANGE_AVG = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hi_24"] = df["h"].rolling(LOOKBACK, min_periods=LOOKBACK).max().shift(1)
    df["lo_24"] = df["l"].rolling(LOOKBACK, min_periods=LOOKBACK).min().shift(1)
    rng = df["h"].rolling(LOOKBACK, min_periods=LOOKBACK).max() - df["l"].rolling(
        LOOKBACK, min_periods=LOOKBACK).min()
    df["range_expanded"] = rng > RANGE_MULT * rng.rolling(RANGE_AVG, min_periods=RANGE_AVG).mean()
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
