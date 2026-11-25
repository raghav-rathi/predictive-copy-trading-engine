"""Percentage Price Oscillator signals.

Long when PPO crosses above its signal line while PPO is
positive (uptrend momentum turning up); short when PPO
crosses below its signal line while PPO is negative.
Exit on the opposite signal-line cross. Signal columns are
boolean, no NaN, no lookahead (execution at next-bar open
is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cross_up = crossed_above(df["ppo"], df["ppo_signal"]).fillna(False)
    cross_dn = crossed_below(df["ppo"], df["ppo_signal"]).fillna(False)
    df["long_entry"] = (cross_up & (df["ppo"] > 0)).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & (df["ppo"] < 0)).fillna(False).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
