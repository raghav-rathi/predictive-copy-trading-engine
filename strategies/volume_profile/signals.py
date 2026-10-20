"""Volume profile value-area fade signals.

Failed-auction fades at the value-area edges:

Long:  the prior bar's close dipped below VAL (failed breakdown) and
       the current bar closes back above that VAL -> long.
Short: the prior bar's close spiked above VAH (failed breakout) and
       the current bar closes back below that VAH -> short.

VAL/VAH come from the prior bar's profile so the trigger level is
known before the entry bar closes. Exits: none from the signal side —
the risk config manages the trade (2xATR stop, 3xATR target as a VAH
proxy, 120-bar max hold).
"""

from __future__ import annotations

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    val_prev = df["vp_val"].shift(1)
    vah_prev = df["vp_vah"].shift(1)
    prev_c = df["c"].shift(1)

    failed_breakdown = (prev_c < val_prev) & (df["c"] > val_prev)
    failed_breakout = (prev_c > vah_prev) & (df["c"] < vah_prev)

    out["long_entry"] = failed_breakdown.fillna(False).astype(bool)
    out["short_entry"] = (failed_breakout & ~failed_breakdown).fillna(False).astype(bool)
    out["long_exit"] = pd.Series(False, index=df.index)
    out["short_exit"] = pd.Series(False, index=df.index)
    return out
