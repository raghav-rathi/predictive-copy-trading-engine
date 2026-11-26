"""Donchian channel breakout + Stochastic filter indicators.

Richard Donchian's channel: the highest high and lowest low
of the last n periods (n = 20 by default; the Turtle exit
channel is n = 10). Stochastic(14,3,3) per the George Lane
convention in stochastic_macd_combo: %K = 100 * (close -
lowest low(14)) / (highest high(14) - lowest low(14));
%D = SMA(%K, 3). When the 14-bar high-low range is zero
(flat bars) %K is set to 50.0 (neutral) instead of dividing
by zero.

Columns:
    donchian_high_20, donchian_low_20 -- 20-bar entry channel
    donchian_high_10, donchian_low_10 -- 10-bar Turtle exit channel
    stoch_k, stoch_d                   -- Stochastic %K(14), %D(3)
    atr14                              -- ATR(14), diagnostic

No lookahead: rolling extremes and causal SMAs; the signals
shift the channels by one bar so a breakout is judged
against the prior bars' channel, never the current bar's
own high/low.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ENTRY_N = 20
EXIT_N = 10
K_PERIOD = 14
D_PERIOD = 3


def add_indicators(
    df: pd.DataFrame,
    entry_n: int = ENTRY_N,
    exit_n: int = EXIT_N,
    k_period: int = K_PERIOD,
    d_period: int = D_PERIOD,
) -> pd.DataFrame:
    df = df.copy()
    d_entry = B.donchian(df["h"], df["l"], entry_n)
    df[f"donchian_high_{entry_n}"] = d_entry[f"donchian_high_{entry_n}"]
    df[f"donchian_low_{entry_n}"] = d_entry[f"donchian_low_{entry_n}"]
    d_exit = B.donchian(df["h"], df["l"], exit_n)
    df[f"donchian_high_{exit_n}"] = d_exit[f"donchian_high_{exit_n}"]
    df[f"donchian_low_{exit_n}"] = d_exit[f"donchian_low_{exit_n}"]
    low_n = df["l"].rolling(k_period, min_periods=k_period).min()
    high_n = df["h"].rolling(k_period, min_periods=k_period).max()
    rng = high_n - low_n
    k = 100.0 * (df["c"] - low_n) / rng
    df["stoch_k"] = k.where(rng > 0, 50.0)
    df["stoch_d"] = B.sma(df["stoch_k"], d_period)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
