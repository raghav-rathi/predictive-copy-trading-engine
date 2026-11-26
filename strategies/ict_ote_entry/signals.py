"""ICT Optimal Trade Entry (OTE) signals.

Long: a bullish setup is armed (see indicators.py) and the close
retraces into the OTE zone (62-79% of the displacement leg).
Short: mirror -- an armed bearish setup and the close retraces
into its OTE zone.
Exit: the close goes beyond 100% of the leg (below the sweep
extreme for a long, above it for a short) or the opposite
setup's entry fires. The house 2xATR hard stop / 3xATR trail
and 120-bar max hold sit behind these exits.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness). The exit leg
start is the sweep extreme of the setup that produced the
entry, tracked bar by bar; an exit is only judged against a
leg that was already entered, never a pending setup.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy(float)
    long_entry = (
        df["ote_long_armed"]
        & (df["c"] >= df["ote_long_zone_lo"])
        & (df["c"] <= df["ote_long_zone_hi"])
    ).fillna(False).to_numpy(bool)
    short_entry = (
        df["ote_short_armed"]
        & (df["c"] >= df["ote_short_zone_lo"])
        & (df["c"] <= df["ote_short_zone_hi"])
    ).fillna(False).to_numpy(bool)
    leg_start_l = df["ote_long_leg_start"].to_numpy(float)
    leg_start_s = df["ote_short_leg_start"].to_numpy(float)
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
