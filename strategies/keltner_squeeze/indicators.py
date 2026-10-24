"""TTM-style squeeze indicators: Bollinger Bands inside Keltner Channels.

    bb_mid/upper/lower -- SMA(close, 20) +/- 2.0 * SD(close, 20)
    kc_mid/upper/lower -- EMA(close, 20) +/- 1.5 * ATR(10)
    squeeze_on         -- bb_width < kc_width

When the Bollinger Bands contract inside the Keltner Channels,
volatility has compressed to the point where the next expansion
tends to be directional — the classic TTM Squeeze setup (John
Carter). The squeeze itself says nothing about direction; the
breakout bar does.

Columns:

    bb_mid, bb_upper, bb_lower, bb_width -- Bollinger Band(20, 2.0)
    kc_mid, kc_upper, kc_lower, kc_width -- Keltner Channel(EMA20, 1.5xATR10)
    squeeze_on -- True while Bollinger width < Keltner width
    atr    -- Wilder ATR(14) for the risk layer

No lookahead: all windows are trailing (min_periods=n). Note the
Keltner ATR uses a 10-bar window while the risk layer uses ATR(14);
the two serve different purposes and are intentionally different.
"""

import pandas as pd

from strategies import base as B

BB_N = 20        # shipped defaults (fixed a priori)
BB_K = 2.0
KC_EMA_N = 20
KC_ATR_N = 10
KC_K = 1.5


def add_indicators(df: pd.DataFrame, bb_n: int = BB_N, bb_k: float = BB_K,
                   kc_ema_n: int = KC_EMA_N, kc_atr_n: int = KC_ATR_N,
                   kc_k: float = KC_K) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], bb_n, bb_k)
    df["bb_mid"] = bb["bb_mid"]
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_width"] = bb["bb_width"]
    kc = B.keltner(df["h"], df["l"], df["c"], kc_ema_n, kc_atr_n, kc_k)
    df["kc_mid"] = kc["kc_mid"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["kc_width"] = df["kc_upper"] - df["kc_lower"]
    df["squeeze_on"] = (df["bb_width"] < df["kc_width"]).fillna(False)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
