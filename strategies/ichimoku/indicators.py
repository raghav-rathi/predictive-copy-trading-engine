"""Ichimoku Cloud indicators (Goichi Hosoda, public rules).

Components: Tenkan(9), Kijun(26), Senkou A/B (cloud, shifted +26),
Chikou (lagging, shifted -26). Classic trend system: price vs cloud
defines regime, Tenkan/Kijun cross triggers, Chikou confirms no
overhead resistance.
"""

import pandas as pd

from strategies import base as B

TENKAN = 9
KIJUN = 26
SENKOU = 52


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ich = B.ichimoku(df["h"], df["l"], df["c"], TENKAN, KIJUN, SENKOU)
    df["tenkan"] = ich["tenkan"]
    df["kijun"] = ich["kijun"]
    df["senkou_a"] = ich["senkou_a"]
    df["senkou_b"] = ich["senkou_b"]
    df["chikou"] = ich["chikou"]
    df["cloud_top"] = df[["senkou_a", "senkou_b"]].max(axis=1)
    df["cloud_bot"] = df[["senkou_a", "senkou_b"]].min(axis=1)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
