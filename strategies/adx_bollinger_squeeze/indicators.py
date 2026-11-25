"""Bollinger squeeze + ADX expansion indicators.

Bollinger Bands (20, 2.0) via base.bollinger; bandwidth is the
band width relative to the mid-band:

    bandwidth_t = (upper_t - lower_t) / mid_t

A squeeze is bandwidth at its 20-bar minimum (bandwidth ==
its rolling 20-bar min, exact float equality against the same
series). ADX(14) via base.adx measures whether the expansion
that follows has trend strength behind it.

Columns:
    bb_mid, bb_upper, bb_lower -- Bollinger Bands (20, 2.0)
    bandwidth                  -- (upper - lower) / mid
    bandwidth_min              -- rolling 20-bar minimum of bandwidth
    squeeze                    -- bandwidth == bandwidth_min
    adx, plus_di, minus_di     -- Wilder ADX(14) and directionals
    atr14                      -- ATR(14), diagnostic

No lookahead: every value on bar j uses data through bar j's
close only (rolling windows and Wilder smoothing are causal).
"""

import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
SQUEEZE_WINDOW = 20
ADX_N = 14


def add_indicators(
    df: pd.DataFrame,
    bb_n: int = BB_N,
    bb_k: float = BB_K,
    squeeze_window: int = SQUEEZE_WINDOW,
    adx_n: int = ADX_N,
) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], bb_n, bb_k)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bandwidth"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_mid"]
    df["bandwidth_min"] = df["bandwidth"].rolling(
        squeeze_window, min_periods=squeeze_window
    ).min()
    df["squeeze"] = (df["bandwidth"] == df["bandwidth_min"]).fillna(False).astype(bool)
    adx = B.adx(df["h"], df["l"], df["c"], adx_n)
    df["adx"] = adx["adx"]
    df["plus_di"] = adx["plus_di"]
    df["minus_di"] = adx["minus_di"]
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
