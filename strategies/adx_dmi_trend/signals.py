"""Wilder ADX/DMI trend-system signals.

LONG when +DI crosses above -DI while ADX(14) > 25; SHORT on the
mirror cross (-DI above +DI) while ADX > 25. The harness executes
at the next bar's open.

Exits (state machine, one pass):
- Long: the opposite cross (-DI crosses above +DI) OR ADX falling
  below 20.
- Short: the opposite cross (+DI crosses above -DI) OR ADX
  falling below 20.
- Opposite setup while in a position flips it (exit + entry on
  the same bar): an opposite cross is by construction the long
  exit condition, so the flip is the natural consequence of the
  exit rule, made explicit here.

Transition-only entries: a setup bar while already holding the
same side does not re-enter. All conditions read bar-i values at
bar i; signal columns are boolean, no NaN, no lookahead.
"""

import numpy as np
import pandas as pd

from strategies import base as B

ADX_EXIT = 20.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    adx = df["adx"].to_numpy(dtype=float)
    plus_di = df["plus_di"].to_numpy(dtype=float)
    minus_di = df["minus_di"].to_numpy(dtype=float)
    long_setup = df["long_setup"].fillna(False).to_numpy(dtype=bool)
    short_setup = df["short_setup"].fillna(False).to_numpy(dtype=bool)

    # Opposite crosses, computed from the DI columns (transition
    # only; NaN comparisons are False).
    opp_for_long = B.crossed_above(df["minus_di"], df["plus_di"]).fillna(False).to_numpy(dtype=bool)
    opp_for_short = B.crossed_above(df["plus_di"], df["minus_di"]).fillna(False).to_numpy(dtype=bool)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        if pos == "long":
            # adx[i] < 20 is False while ADX is NaN, so no exit can
            # fire on an unseeded bar.
            if opp_for_long[i] or adx[i] < ADX_EXIT:
                lx[i] = True
                pos = None
                if short_setup[i]:
                    se[i] = True
                    pos = "short"
        elif pos == "short":
            if opp_for_short[i] or adx[i] < ADX_EXIT:
                sx[i] = True
                pos = None
                if long_setup[i]:
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
