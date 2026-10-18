"""Elder Impulse System indicators (Alexander Elder, "Come Into My Trading Room").

Impulse color per bar (no lookahead: every value on bar i uses bars through
i only):
  * green: EMA(13) rising (ema > ema[1]) AND MACD(12,26,9) histogram rising
  * red:   EMA(13) falling AND MACD histogram falling
  * blue:  everything else (mixed) — no trade allowed
"""

import numpy as np
import pandas as pd

from strategies import base as B

EMA_LEN = 13
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9


def add_indicators(
    df: pd.DataFrame,
    ema_len: int = EMA_LEN,
    macd_fast: int = MACD_FAST,
    macd_slow: int = MACD_SLOW,
    macd_signal: int = MACD_SIGNAL,
) -> pd.DataFrame:
    df = df.copy()
    ema = B.ema(df["c"], ema_len)
    df["impulse_ema"] = ema
    hist = B.macd(df["c"], macd_fast, macd_slow, macd_signal)["macd_hist"]
    df["impulse_hist"] = hist
    ema_up = (ema > ema.shift(1)).fillna(False)
    ema_dn = (ema < ema.shift(1)).fillna(False)
    hist_up = (hist > hist.shift(1)).fillna(False)
    hist_dn = (hist < hist.shift(1)).fillna(False)
    color = np.select(
        [ema_up & hist_up, ema_dn & hist_dn],
        ["green", "red"],
        default="blue",
    )
    df["impulse_color"] = pd.Series(color, index=df.index)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
