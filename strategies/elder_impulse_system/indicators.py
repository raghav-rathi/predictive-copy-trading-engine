"""Elder Impulse System indicators (Alexander Elder, 2002).

Green bar = EMA(13) rising AND MACD histogram (12,26,9) rising.
Red bar   = EMA(13) falling AND MACD histogram falling.
Blue bar  = disagreement between the two.
"""

import pandas as pd

from strategies import base as B

EMA_PERIOD = 13

INDICATOR_COLS = ["ema13", "macd", "macd_signal", "macd_hist",
                  "ema_rising", "hist_rising", "impulse_green", "impulse_red"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema13"] = B.ema(df["c"], EMA_PERIOD)
    m = B.macd(df["c"], 12, 26, 9)
    df["macd"] = m["macd"]
    df["macd_signal"] = m["macd_signal"]
    df["macd_hist"] = m["macd_hist"]
    df["ema_rising"] = (df["ema13"] > df["ema13"].shift(1)).astype(bool)
    df["hist_rising"] = (df["macd_hist"] > df["macd_hist"].shift(1)).astype(bool)
    df["impulse_green"] = (df["ema_rising"] & df["hist_rising"]).astype(bool)
    df["impulse_red"] = ((~df["ema_rising"]) & (~df["hist_rising"])).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
