"""Donchian Turtle Breakout (System 1) indicators (causal, no lookahead).

The Donchian channel for bar i is built ONLY from the 20 (entry)
or 10 (exit) bars BEFORE bar i. ``base.donchian`` computes the
rolling max/min including the current bar, so every channel here
is shifted by one bar:

    prior_high_20[i] = max(h[i-20 : i])   (bars i-20 .. i-1)
    prior_low_20[i]  = min(l[i-20 : i])
    prior_high_10[i] = max(h[i-10 : i])
    prior_low_10[i]  = min(l[i-10 : i])

A close ABOVE the prior 20-bar high is a long breakout; a close
BELOW the prior 20-bar low is a short breakout. Because the
channel excludes bar i, a bar can never break out on its own
high/low — the breakout is a genuine close through a level that
was known before the bar opened.

Seeding: the prior channels are NaN for the first 20 bars (10
for the exit channel) and ATR(20) is NaN for the first 20 bars;
breakout/exit booleans are False there (``fillna(False)``), so no
signal column ever carries NaN. WARMUP = 60 bars covers all of
it with margin.
"""

import pandas as pd

from strategies import base as B

ENTRY_N = 20
EXIT_N = 10
ATR_N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]

    dc20 = B.donchian(h, l, ENTRY_N)
    dc10 = B.donchian(h, l, EXIT_N)
    # Shift by 1: channel of the N bars BEFORE bar i, excluding bar i.
    df["donchian_high_20"] = dc20[f"donchian_high_{ENTRY_N}"].shift(1)
    df["donchian_low_20"] = dc20[f"donchian_low_{ENTRY_N}"].shift(1)
    df["donchian_high_10"] = dc10[f"donchian_high_{EXIT_N}"].shift(1)
    df["donchian_low_10"] = dc10[f"donchian_low_{EXIT_N}"].shift(1)

    df["atr20"] = B.atr(h, l, c, ATR_N)
    df["atr"] = df["atr20"]

    df["long_breakout"] = (
        (c > df["donchian_high_20"]).fillna(False).astype(bool)
    )
    df["short_breakout"] = (
        (c < df["donchian_low_20"]).fillna(False).astype(bool)
    )
    df["long_exit_cond"] = (
        (c < df["donchian_low_10"]).fillna(False).astype(bool)
    )
    df["short_exit_cond"] = (
        (c > df["donchian_high_10"]).fillna(False).astype(bool)
    )
    return df
