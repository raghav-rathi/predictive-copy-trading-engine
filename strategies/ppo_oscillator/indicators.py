"""Percentage Price Oscillator indicators (StockCharts ChartSchool).

PPO is MACD expressed in percentage terms, so its readings are
comparable across securities and across price levels:

    PPO    = 100 * (EMA(12) - EMA(26)) / EMA(26)
    signal = EMA(PPO, 9)
    hist   = PPO - signal

Columns:
    ppo        -- Percentage Price Oscillator (percent)
    ppo_signal -- 9-period EMA of PPO
    ppo_hist   -- PPO minus its signal line

No lookahead: every value on bar j uses closes through bar j
only (causal EMAs).
"""

import pandas as pd

from strategies import base as B

FAST = 12    # shipped default (StockCharts standard)
SLOW = 26    # shipped default (StockCharts standard)
SIGNAL = 9   # shipped default (StockCharts standard)


def add_indicators(
    df: pd.DataFrame,
    fast: int = FAST,
    slow: int = SLOW,
    signal: int = SIGNAL,
) -> pd.DataFrame:
    df = df.copy()
    ema_fast = B.ema(df["c"], fast)
    ema_slow = B.ema(df["c"], slow)
    df["ppo"] = 100.0 * (ema_fast - ema_slow) / ema_slow
    df["ppo_signal"] = B.ema(df["ppo"], signal)
    df["ppo_hist"] = df["ppo"] - df["ppo_signal"]
    return df
