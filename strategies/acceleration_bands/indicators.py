"""Acceleration Bands indicators (Price Headley, published form).

Upper = SMA(20) of high * (1 + 4 * (high - low) / (high + low))
Lower = SMA(20) of low  * (1 - 4 * (high - low) / (high + low))
Mid   = SMA(20) of close
"""

import pandas as pd

from strategies import base as B

PERIOD = 20
FACTOR = 4.0
INDICATOR_COLS = ["ab_upper", "ab_lower", "ab_mid"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rng = (df["h"] - df["l"]) / (df["h"] + df["l"]).replace(0, float("nan"))
    rng = rng.fillna(0.0)
    df["ab_upper"] = B.sma(df["h"] * (1 + FACTOR * rng), PERIOD)
    df["ab_lower"] = B.sma(df["l"] * (1 - FACTOR * rng), PERIOD)
    df["ab_mid"] = B.sma(df["c"], PERIOD)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
