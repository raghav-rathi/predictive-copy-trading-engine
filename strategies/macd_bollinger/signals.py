"""MACD Bollinger-band-edge signals.

Long entry: the MACD line crosses back UP through its own lower
Bollinger Band while still below zero — the oversold MACD
excursion is releasing, not deepening. The zero condition keeps
the trade on the oversold side; a MACD already above zero
crossing its lower band is a mid-trend wobble, not a release.

Short entry: mirror — MACD crosses back DOWN through its own
upper band while still above zero.

Exits: the MACD line crosses its own band midline in the adverse
direction (the release has run its course back to the mean), or
crosses its signal line in the adverse direction, whichever
comes first. Both exit conditions are one-sided crosses, so an
exit can only fire after the line first travelled to the other
side of the trigger level.

All conditions read bar-i closes; the harness executes at bar
i+1's open. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    macd = df["macd"]
    sig = df["macd_signal"]
    mid = df["macd_bb_mid"]
    upper = df["macd_bb_upper"]
    lower = df["macd_bb_lower"]

    df["long_entry"] = (crossed_above(macd, lower) & (macd < 0)).fillna(False).astype(bool)
    df["short_entry"] = (crossed_below(macd, upper) & (macd > 0)).fillna(False).astype(bool)
    df["long_exit"] = (
        crossed_below(macd, mid) | crossed_below(macd, sig)
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        crossed_above(macd, mid) | crossed_above(macd, sig)
    ).fillna(False).astype(bool)
    return df
