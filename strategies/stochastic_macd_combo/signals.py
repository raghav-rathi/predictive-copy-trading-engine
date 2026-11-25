"""Stochastic + MACD dual-confirmation signals.

The Stochastic %K/%D cross is the trigger; the MACD histogram
sign is the trend filter, so a cross only trades when MACD
agrees with its direction.

Long when %K crosses above %D while %K < 30 (oversold cross)
AND MACD histogram > 0; short when %K crosses below %D while
%K > 70 (overbought cross) AND MACD histogram < 0. Exit on
the opposite Stochastic cross OR the MACD histogram flipping
sign. Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    d = df["stoch_d"]
    hist = df["macd_hist"]
    cross_up = crossed_above(k, d).fillna(False)
    cross_dn = crossed_below(k, d).fillna(False)
    df["long_entry"] = (
        cross_up & (k < 30) & (hist > 0)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        cross_dn & (k > 70) & (hist < 0)
    ).fillna(False).astype(bool)
    df["long_exit"] = (cross_dn | (hist < 0)).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | (hist > 0)).fillna(False).astype(bool)
    return df
