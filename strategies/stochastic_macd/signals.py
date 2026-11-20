"""Stochastic %K/%D cross + MACD histogram agreement signals.

Long entry:  %K crosses above %D while %K < 30 (cross out of
             oversold) AND MACD histogram > 0.
Short entry: %K crosses below %D while %K > 70 (cross out of
             overbought) AND MACD histogram < 0.
Long exit:   %K crosses below %D OR MACD histogram flips negative.
Short exit:  %K crosses above %D OR MACD histogram flips positive.

The cross is evaluated on bar i using %K/%D values through bar i's
close only (crossed_above/below compare bar i with bar i-1). Signal
columns are boolean, no NaN, no lookahead (the harness executes at
the next bar's open).
"""

import pandas as pd

from strategies import base as B

# %K thresholds for the cross-out-of-extreme entry gate (shipped values).
K_OVERSOLD = 30
K_OVERBOUGHT = 70


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    d = df["stoch_d"]
    hist = df["macd_hist"]
    cross_up = B.crossed_above(k, d).fillna(False).astype(bool)
    cross_down = B.crossed_below(k, d).fillna(False).astype(bool)
    hist_pos = (hist > 0).fillna(False)
    hist_neg = (hist < 0).fillna(False)
    df["long_entry"] = (cross_up & (k < K_OVERSOLD) & hist_pos).fillna(False).astype(bool)
    df["short_entry"] = (cross_down & (k > K_OVERBOUGHT) & hist_neg).fillna(False).astype(bool)
    df["long_exit"] = (cross_down | hist_neg).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | hist_pos).fillna(False).astype(bool)
    return df
