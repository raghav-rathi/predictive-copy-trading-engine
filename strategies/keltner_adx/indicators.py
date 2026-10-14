"""Keltner Channel + ADX indicators (Chester Keltner, Linda Raschke variant).

Keltner Channels: EMA(20) +/- 1.5xATR(10) — an ATR envelope around trend.
ADX(14) > 25 regime filter: only take channel breakouts when trend strength
is confirmed. Breakout + trend-strength is the classic combo.
"""

import pandas as pd

from strategies import base as B

KC_EMA = 20
KC_ATR = 10
KC_K = 1.5
ADX_MIN = 25.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    kc = B.keltner(df["h"], df["l"], df["c"], KC_EMA, KC_ATR, KC_K)
    df["kc_upper"] = kc["kc_upper"]
    df["kc_lower"] = kc["kc_lower"]
    df["kc_mid"] = kc["kc_mid"]
    df["adx"] = B.adx(df["h"], df["l"], df["c"], 14)["adx"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
