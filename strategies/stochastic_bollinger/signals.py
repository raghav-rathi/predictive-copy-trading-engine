"""Stochastic + Bollinger %b signals (mean reversion into the band).

LONG on %K crossing above %D (transition) while %b < 0.2 (price
near the lower Bollinger Band) and %K < 30 (oversold) — a double-
oversold gate: price is at the band AND momentum is washed out.
SHORT on the mirror: %K crossing below %D while %b > 0.8 and
%K > 70.

Exits (state machine, transition-only entries, no re-entry on a
held state):
- Long: %b > 0.8 (price reached the upper band — the reversion
  is complete) OR %K crosses below %D (momentum rolled over).
- Short: %b < 0.2 OR %K crosses above %D.
- An opposite entry condition while in a position flips it
  (exit + entry on the same bar); note the short-entry condition
  (%K cross below %D) is itself a long-exit condition, so a flip
  is the natural outcome, not a special case.

This is a mean-reversion-into-band setup, NOT a band-breakout
system: entries are taken at the lower/upper band expecting a
return toward the mid-band, and exits are taken at the opposite
band. In a strong trend %b can pin near 0 or 1 for many bars
while %K stays oversold/overbought — the cross requirement is
the only thing that keeps the system from buying every bar of
a downtrend.

All conditions read bar-i values at bar i; signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import numpy as np
import pandas as pd

from strategies import base as B
from strategies.stochastic_bollinger.indicators import (
    PCTB_OVERBOUGHT,
    PCTB_OVERSOLD,
    STOCH_OVERBOUGHT,
    STOCH_OVERSOLD,
)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    pct_b = df["pct_b"].to_numpy(dtype=float)
    k = df["stoch_k"].to_numpy(dtype=float)
    d = df["stoch_d"].to_numpy(dtype=float)

    k_cross_up = B.crossed_above(df["stoch_k"], df["stoch_d"]).fillna(False).to_numpy(dtype=bool)
    k_cross_down = B.crossed_below(df["stoch_k"], df["stoch_d"]).fillna(False).to_numpy(dtype=bool)

    long_setup = k_cross_up & (pct_b < PCTB_OVERSOLD) & (k < STOCH_OVERSOLD)
    short_setup = k_cross_down & (pct_b > PCTB_OVERBOUGHT) & (k > STOCH_OVERBOUGHT)
    long_exit_cond = (pct_b > PCTB_OVERBOUGHT) | k_cross_down
    short_exit_cond = (pct_b < PCTB_OVERSOLD) | k_cross_up

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            if long_exit_cond[i]:
                lx[i] = True
                pos = None
            elif short_setup[i]:
                lx[i] = True
                se[i] = True
                pos = "short"
        elif pos == "short":
            if short_exit_cond[i]:
                sx[i] = True
                pos = None
            elif long_setup[i]:
                sx[i] = True
                le[i] = True
                pos = "long"
        if pos is None:
            if long_setup[i]:
                le[i] = True
                pos = "long"
            elif short_setup[i]:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
