"""RSI(14) + volume-confirmation indicators.

Long: RSI crosses above 50 AND volume > 1.25x the trailing 20-bar
mean volume (previous 20 bars, shifted by 1).
Short: RSI crosses below 50 AND volume > 1.25x mean volume.

RSI uses Wilder smoothing (strategies.base.rsi). The volume mean
excludes the current bar so the bar's own volume does not dilute
the comparison.

Columns:
    rsi          -- Wilder RSI(14)
    vol_mean_20  -- mean volume of the previous 20 bars
    vol_ratio    -- volume / vol_mean_20
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: every value on bar i uses data through bar i's close.
"""

import pandas as pd

from strategies import base as B

RSI_N = 14
VOL_N = 20
VOL_MULT = 1.25

INDICATOR_COLS = ["rsi", "vol_mean_20", "vol_ratio", "atr"]


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_N,
                   vol_n: int = VOL_N) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["vol_mean_20"] = df["v"].rolling(vol_n, min_periods=vol_n).mean().shift(1)
    df["vol_ratio"] = df["v"] / df["vol_mean_20"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
