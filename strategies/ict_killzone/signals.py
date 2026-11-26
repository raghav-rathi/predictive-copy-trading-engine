"""ICT killzone signals.

Long: a bullish setup is armed (see indicators.py) and the
close crosses below the 50% level of the displacement leg
(the FVG-midpoint approximation). Short: mirror -- an armed
bearish setup and the close crosses above the 50% level.
Exit: the close goes beyond the leg start (below the sweep
extreme for a long, above it for a short -- the opposite
sweep) or the opposite setup's entry fires. The house 2xATR
hard stop / 3xATR trail sit behind these exits, and the
24-bar max hold enforces the intraday design.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness). No NEW setup may
start outside the two killzone windows: the armed flag is
only ever raised by a sweep + displacement that both
completed inside a window. Deviation (see indicators.py):
windows include their end-hour bar, and an armed setup's
retracement entry may land after its window closes,
expiring at the UTC day boundary instead -- the strict
reading is unfireable on 1h bars (minimum 4-bar sequence
vs 3-bar London / 2-bar NY windows). The exit leg
start is the sweep extreme of the setup that produced the
entry, tracked bar by bar.
"""

import numpy as np
import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(float)
    long_entry = (
        df["kz_long_armed"] & crossed_below(df["c"], df["kz_long_mid"])
    ).fillna(False).to_numpy(bool)
    short_entry = (
        df["kz_short_armed"] & crossed_above(df["c"], df["kz_short_mid"])
    ).fillna(False).to_numpy(bool)
    leg_start_l = df["kz_long_leg_start"].to_numpy(float)
    leg_start_s = df["kz_short_leg_start"].to_numpy(float)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    held_leg_l = None
    held_leg_s = None
    for i in range(n):
        # Exits are judged against legs entered on earlier bars.
        if held_leg_l is not None and (c[i] < held_leg_l or short_entry[i]):
            long_exit[i] = True
            held_leg_l = None
        if held_leg_s is not None and (c[i] > held_leg_s or long_entry[i]):
            short_exit[i] = True
            held_leg_s = None
        if long_entry[i]:
            held_leg_l = leg_start_l[i]
        if short_entry[i]:
            held_leg_s = leg_start_s[i]
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
