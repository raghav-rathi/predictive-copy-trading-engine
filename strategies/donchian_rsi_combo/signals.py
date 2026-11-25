"""Donchian channel breakout + RSI filter signals.

Long: close crosses above the 20-bar Donchian high of the prior
bars (the channel value shifted by 1, so the breakout is vs the
prior 20 bars, never the current bar's own high) AND RSI < 70.
Short: close crosses below the 20-bar Donchian low of the prior
bars AND RSI > 30.
Exit (classic Turtle): long exits when the close falls below
the 10-bar Donchian low, short exits when the close rises
above the 10-bar Donchian high — both judged against the
prior bars' channel (shifted by 1). The shift is required:
the unshifted 10-bar low includes the current bar's own low,
and the close can never be below it, so the unshifted reading
could never fire.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

RSI_LONG_MAX = 70.0
RSI_SHORT_MIN = 30.0


def add_signals(
    df: pd.DataFrame,
    rsi_long_max: float = RSI_LONG_MAX,
    rsi_short_min: float = RSI_SHORT_MIN,
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
    rsi = df["rsi"]
    df["long_entry"] = (
        crossed_above(df["c"], prior_high) & (rsi < rsi_long_max)
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        crossed_below(df["c"], prior_low) & (rsi > rsi_short_min)
    ).fillna(False).astype(bool)
    df["long_exit"] = (df["c"] < exit_low).fillna(False).astype(bool)
    df["short_exit"] = (df["c"] > exit_high).fillna(False).astype(bool)
    return df
