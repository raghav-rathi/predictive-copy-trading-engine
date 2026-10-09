"""Bollinger Band squeeze indicators (TTM-squeeze mechanics, public).

Squeeze = Bollinger Bands(20, 2) inside Keltner Channels(20, 1.5):
volatility compression. The trade is the expansion: when the squeeze
releases, enter in the direction of the break with momentum confirmation.
"""

import pandas as pd

from strategies import base as B

BB_N = 20
BB_K = 2.0
KC_EMA = 20
KC_ATR = 10
KC_K = 1.5


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bb = B.bollinger(df["c"], BB_N, BB_K)
    kc = B.keltner(df["h"], df["l"], df["c"], KC_EMA, KC_ATR, KC_K)
    df["bb_upper"] = bb["bb_upper"]
    df["bb_lower"] = bb["bb_lower"]
    df["bb_mid"] = bb["bb_mid"]
    df["bb_width"] = bb["bb_width"]
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["kc_mid"] = kc["kc_mid"]
    df["squeeze"] = (df["bb_upper"] < df["kc_upper"]) & (df["bb_lower"] > df["kc_lower"])
    df["squeeze_prev"] = df["squeeze"].shift(1)
    df["mom"] = df["c"] - df["c"].shift(12)  # 12-bar momentum for direction
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
