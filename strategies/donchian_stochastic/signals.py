"""Donchian channel breakout + Stochastic filter signals.

Long: close crosses above the 20-bar Donchian high of the
prior bars (the channel value shifted by 1, so the breakout
is vs the prior 20 bars, never the current bar's own high)
AND %K > %D (momentum rising) AND %K < 80 (not already
overbought). Short: close crosses below the 20-bar Donchian
low of the prior bars AND %K < %D AND %K > 20.
Exit (classic Turtle plus momentum): long exits when the
close falls below the prior 10-bar Donchian low OR %K
crosses below %D; short exits when the close rises above
the prior 10-bar Donchian high OR %K crosses above %D —
both channel legs judged against the prior bars' channel
(shifted by 1). The shift is required: the unshifted 10-bar
low includes the current bar's own low, and the close can
never be below it, so the unshifted reading could never fire.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

K_OVERBOUGHT = 80.0
K_OVERSOLD = 20.0


def add_signals(
    df: pd.DataFrame,
    k_overbought: float = K_OVERBOUGHT,
    k_oversold: float = K_OVERSOLD,
    entry_n: int = 20,
    exit_n: int = 10,
) -> pd.DataFrame:
    df = df.copy()
    # Prior-bar channels: the rolling extreme through bar i-1, so a
    # close on bar i that breaks it is a genuine new extreme.
    prior_high = df[f"donchian_high_{entry_n}"].shift(1)
    prior_low = df[f"donchian_low_{entry_n}"].shift(1)
    exit_low = df[f"donchian_low_{exit_n}"].shift(1)
    exit_high = df[f"donchian_high_{exit_n}"].shift(1)
    k = df["stoch_k"]
    d = df["stoch_d"]
    cross_k_up = crossed_above(k, d)
    cross_k_down = crossed_below(k, d)
    df["long_entry"] = (
        crossed_above(df["c"], prior_high) & (k > d) & (k < k_overbought)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        crossed_below(df["c"], prior_low) & (k < d) & (k > k_oversold)
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        (df["c"] < exit_low) | cross_k_down
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (df["c"] > exit_high) | cross_k_up
    ).fillna(False).astype(bool)
    return df
