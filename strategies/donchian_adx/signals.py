"""Donchian 20 breakout signals with an ADX(14) > 25 trend filter.

Long entry:  close above the prior 20-bar highest high AND ADX(14) > 25.
Short entry: close below the prior 20-bar lowest low AND ADX(14) > 25.
Long exit:   ADX(14) falls below 20 OR the opposite breakout
             (close below the prior 20-bar lowest low).
Short exit:  ADX(14) falls below 20 OR the opposite breakout
             (close above the prior 20-bar highest high).

This is deliberately an ADX-filtered variant of `donchian_channel`
(precedent: keltner_adx vs keltner_breakout): the plain Donchian
breakout trades every 20-bar extreme, while this one only trades
breakouts that occur while a measurable trend is already in force,
and exits when trend strength decays even if price has not reversed.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.donchian_adx.indicators import ADX_ENTRY, ADX_EXIT


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hi = df["donchian_high_20"].shift(1)
    lo = df["donchian_low_20"].shift(1)
    adx = df["adx"]
    trend = (adx > ADX_ENTRY).fillna(False)
    weak = (adx < ADX_EXIT).fillna(False)
    breakout_up = (df["c"] > hi).fillna(False)
    breakout_dn = (df["c"] < lo).fillna(False)
    df["long_entry"] = (breakout_up & trend).astype(bool)
    df["short_entry"] = (breakout_dn & trend).astype(bool)
    df["long_exit"] = (weak | breakout_dn).astype(bool)
    df["short_exit"] = (weak | breakout_up).astype(bool)
    return df
