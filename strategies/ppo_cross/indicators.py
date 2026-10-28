"""Percentage Price Oscillator (PPO) indicators.

PPO normalises the MACD by price, so its readings are comparable
across coins and price regimes:

    ppo        -- (EMA(12) - EMA(26)) / EMA(26) * 100
    ppo_signal -- EMA(9) of ppo
    ppo_hist   -- ppo - ppo_signal
    atr        -- Wilder ATR(14) for the risk layer

All causal: EMAs read only data through the current bar's close.
"""

import pandas as pd

from strategies import base as B

FAST = 12
SLOW = 26
SIGNAL = 9


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    fast = B.ema(df["c"], FAST)
    slow = B.ema(df["c"], SLOW)
    ppo = (fast - slow) / slow * 100.0
    df["ppo"] = ppo
    df["ppo_signal"] = B.ema(ppo, SIGNAL)
    df["ppo_hist"] = ppo - df["ppo_signal"]
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
