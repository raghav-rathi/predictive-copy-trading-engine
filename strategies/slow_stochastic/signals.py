"""Slow Stochastic signals, long/short symmetric.

Entry logic (mirror for shorts):

    long_entry  = crossed_above(%K, %D) & (%K < 20)
    short_entry = crossed_below(%K, %D) & (%K > 80)

The cross is the trigger, the zone is the filter: a bullish
cross only counts while the oscillator is still oversold
(%K < 20) — the turn is happening off a washed-out low, not
mid-range noise. A cross that fires at %K = 50 is just the
oscillator wandering through the middle of its range and is
blocked. The short side mirrors off the overbought zone.

Exits are the pure opposite crosses (no zone filter — once the
trade is on, the exit should be trigger-happy, not gated):

    long_exit  = crossed_below(%K, %D)
    short_exit = crossed_above(%K, %D)

All conditions read bar-j closes at bar j; the harness executes
at the next bar's open. Signal columns are boolean, no NaN, no
lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.slow_stochastic.indicators import OVERSOLD, OVERBOUGHT


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["stoch_k"]
    d = df["stoch_d"]

    xup = crossed_above(k, d).fillna(False)
    xdn = crossed_below(k, d).fillna(False)

    df["long_entry"] = (xup & (k < OVERSOLD).fillna(False)).astype(bool)
    df["short_entry"] = (xdn & (k > OVERBOUGHT).fillna(False)).astype(bool)
    df["long_exit"] = xdn.astype(bool)
    df["short_exit"] = xup.astype(bool)
    return df
