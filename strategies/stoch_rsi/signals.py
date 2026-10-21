"""Stochastic RSI cross signals.

Classic Chande & Kroll usage: the %K line is the trigger, and the
20/80 levels mark oversold/overbought zones (50 is the midline).

Long entry:  %K crosses ABOVE 20 — momentum leaves the oversold zone,
             i.e. downside exhaustion, rather than buying into the
             depths of a dump.
Short entry: %K crosses BELOW 80 — momentum leaves the overbought
             zone (upside exhaustion).

Long exit:  %K crosses below 50 — the midline cross says the bounce
            leg is done; take the mean-reversion profit before %K
            dives back toward oversold.
Short exit: %K crosses above 50 (mirror).

Entries deliberately ignore the %D line: %K alone is the faster
trigger and %D adds lag without materially changing which level
crosses fire. Signal columns are boolean, no NaN, no lookahead
(execution at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

OVERSOLD = 20
OVERBOUGHT = 80
MIDLINE = 50


def _level(df: pd.DataFrame, value: float) -> pd.Series:
    return pd.Series(float(value), index=df.index)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    lv20 = _level(df, OVERSOLD)
    lv80 = _level(df, OVERBOUGHT)
    lv50 = _level(df, MIDLINE)

    long_entry = crossed_above(k, lv20).fillna(False)
    short_entry = crossed_below(k, lv80).fillna(False)
    long_exit = crossed_below(k, lv50).fillna(False)
    short_exit = crossed_above(k, lv50).fillna(False)

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = long_exit.astype(bool)
    df["short_exit"] = short_exit.astype(bool)
    return df
