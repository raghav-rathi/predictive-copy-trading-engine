"""Bollinger squeeze + ADX expansion signals.

Long: a squeeze was true within the last 3 bars AND the close
crosses above the upper Bollinger Band AND ADX > 20.
Short: a squeeze was true within the last 3 bars AND the close
crosses below the lower Bollinger Band AND ADX > 20.
Exit: the close crosses back inside the bands (long: close
crosses below the upper band; short: close crosses above the
lower band) OR ADX falls below 15.

The squeeze itself carries no direction — the breakout side
and the ADX filter pick it. Signal columns are boolean, no
NaN, no lookahead (execution at next-bar open is handled by
the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

ADX_ENTRY = 20.0
ADX_EXIT = 15.0
SQUEEZE_LOOKBACK = 3


def add_signals(
    df: pd.DataFrame,
    adx_entry: float = ADX_ENTRY,
    adx_exit: float = ADX_EXIT,
    squeeze_lookback: int = SQUEEZE_LOOKBACK,
) -> pd.DataFrame:
    df = df.copy()
    sq = df["squeeze"].fillna(False).astype(bool)
    recent = sq.copy()
    for k in range(1, squeeze_lookback):
        recent = recent | sq.shift(k).fillna(False).astype(bool)
    adx = df["adx"]
    strong = (adx > adx_entry).fillna(False)
    weak = (adx < adx_exit).fillna(False)
    df["long_entry"] = (
        recent & crossed_above(df["c"], df["bb_upper"]) & strong
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        recent & crossed_below(df["c"], df["bb_lower"]) & strong
    ).fillna(False).astype(bool)
    df["long_exit"] = (crossed_below(df["c"], df["bb_upper"]) | weak).fillna(False).astype(bool)
    df["short_exit"] = (crossed_above(df["c"], df["bb_lower"]) | weak).fillna(False).astype(bool)
    return df
