"""Fair Value Gap entry/exit signals.

This mechanizes the ICT rule "wait for price to return to the gap, enter
in the impulse direction, stop beyond the far edge":

    long_entry  = an active bullish FVG zone exists
                  AND l[i] < fvg_high (dipped INTO the gap)
                  AND c[i] > fvg_high (closed back above its top edge = rejection)
    short_entry = mirror (h[i] > fvg_low AND c[i] < fvg_low)

The inequalities are strict on purpose: on the formation bar l[i] is
identically equal to fvg_high (and h[i] to fvg_low), so `<` / `>`
exclude the formation bar itself and require a genuine later-bar retest
-- entering on the displacement bar's own close would be trend-chasing,
not the gap-retest the ICT rule describes.

Exits: long_exit fires when the zone is mitigated (the first bar whose
low trades below fvg_low, which is exactly when the zone column flips
from active to NaN) OR on a short_entry (opposite-direction signal).
short_exit mirrors.

Signal columns are boolean, no NaN, no lookahead: bar i's signals read
only data known at bar i's close; the harness executes at the next bar's
open.
"""

import pandas as pd

DISPL_MULT = 1.5  # displacement threshold, fixed a priori (see indicators.py)


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    bull_low = df["fvg_bull_low"]
    bull_high = df["fvg_bull_high"]
    bear_low = df["fvg_bear_low"]
    bear_high = df["fvg_bear_high"]
    l, h, c = df["l"], df["h"], df["c"]

    bull_zone = bull_low.notna()
    bear_zone = bear_low.notna()

    # Strict inequalities exclude the formation bar (l[i] == fvg_high there
    # by construction): entry needs a real dip-into-the-gap plus a close
    # back above the top edge.
    long_entry = bull_zone & (l < bull_high) & (c > bull_high)
    short_entry = bear_zone & (h > bear_low) & (c < bear_low)

    # Mitigation events: the zone was active on the prior bar and this bar
    # traded through its far edge (l < fvg_low / h > fvg_high).
    prev_bull_low = bull_low.shift(1)
    prev_bear_high = bear_high.shift(1)
    bull_mitigated = prev_bull_low.notna() & (l < prev_bull_low)
    bear_mitigated = prev_bear_high.notna() & (h > prev_bear_high)

    long_exit = bull_mitigated | short_entry
    short_exit = bear_mitigated | long_entry

    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
