"""Rob Carver EWMAC forecast indicators (Systematic Trading).

EWMAC rule: raw = EMA(fast) - EMA(slow) of close (strategies.base.ema).
Three rules (8,32), (16,64), (32,128); each z-scored by its own 252-bar
rolling std, then averaged; forecast = clip(10 * combined_z, -20, +20).

No lookahead: every value on bar i uses bars through i only.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RULES = [(8, 32), (16, 64), (32, 128)]
Z_WINDOW = 252
FORECAST_SCALE = 10.0
FORECAST_CAP = 20.0
LONG_THRESHOLD = 10.0
SHORT_THRESHOLD = -10.0


def add_indicators(
    df: pd.DataFrame,
    rules: tuple = tuple(RULES),
    z_window: int = Z_WINDOW,
) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    z_cols = []
    for fast, slow in rules:
        raw = B.ema(c, fast) - B.ema(c, slow)
        df[f"ewmac_raw_{fast}_{slow}"] = raw
        vol = raw.rolling(z_window, min_periods=z_window).std()
        z = raw / vol.replace(0, np.nan)
        df[f"ewmac_z_{fast}_{slow}"] = z
        z_cols.append(f"ewmac_z_{fast}_{slow}")
    combined = df[z_cols].mean(axis=1)
    df["ewmac_combined_z"] = combined
    df["forecast"] = (FORECAST_SCALE * combined).clip(-FORECAST_CAP, FORECAST_CAP)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
