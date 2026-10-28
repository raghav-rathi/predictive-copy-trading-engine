"""PPO / signal-line cross signals.

    long_entry  -- PPO crosses above its EMA(9) signal line
    short_entry -- PPO crosses below its EMA(9) signal line
    long_exit   -- PPO crosses back below its signal line
    short_exit  -- PPO crosses back above its signal line

Same cross logic as the classic MACD signal cross, but on the
percentage-normalised oscillator, so the trigger adapts to the
coin's price level. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ppo = df["ppo"]
    sig = df["ppo_signal"]
    df["long_entry"] = crossed_above(ppo, sig).fillna(False).astype(bool)
    df["short_entry"] = crossed_below(ppo, sig).fillna(False).astype(bool)
    df["long_exit"] = crossed_below(ppo, sig).fillna(False).astype(bool)
    df["short_exit"] = crossed_above(ppo, sig).fillna(False).astype(bool)
    return df
