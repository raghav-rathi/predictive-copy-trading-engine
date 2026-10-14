"""80-20 momentum-candle fade indicators (Linda Raschke, Street Smarts).

Momentum bar = bar range >= 80th percentile of the trailing 20 bar
ranges. The momentum bar's close / high / low are carried forward over
the next 5 bars. No lookahead: percentiles and levels use only bars
through the current close.
"""

import pandas as pd

from strategies import base as B

RANGE_LOOK = 20
PCT = 0.8
ENTRY_WINDOW = 5
PUSH_ATR = 0.5
ATR_N = 14


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = df["h"] - df["l"]
    thresh = rng.rolling(RANGE_LOOK, min_periods=RANGE_LOOK).quantile(PCT)
    df["mom_bar"] = (rng > thresh).fillna(False)
    sig = df["mom_bar"]
    df["mom_close"] = df["c"].where(sig).ffill(limit=ENTRY_WINDOW)
    df["mom_high"] = df["h"].where(sig).ffill(limit=ENTRY_WINDOW)
    df["mom_low"] = df["l"].where(sig).ffill(limit=ENTRY_WINDOW)
    df["mom_up"] = (df["c"] > df["o"]).astype(float).where(sig).ffill(limit=ENTRY_WINDOW)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
