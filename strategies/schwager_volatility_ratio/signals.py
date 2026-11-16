"""Schwager volatility-ratio fade signals.

A wide-ranging bar (VR > 2.0) that closes at its extreme and extends
a 5-bar move is faded -- the burst is treated as exhaustion, not
breakout:

    long_entry  -- VR > 2.0 on a bearish bar (close in the lower 25%
                   of the bar, 5-bar return negative)
    short_entry -- VR > 2.0 on a bullish bar (close in the upper 25%
                   of the bar, 5-bar return positive)
    long_exit   -- the opposite wide bar (a bullish VR > 2.0 bar);
                   the 1.5R target and 10-bar time exit live in risk.py
    short_exit  -- mirror image

Execution note (harness deviation, documented): the spec says "enter
next 1h close", but the harness executes signal entries at the next
bar's *open*, so the effective entry is the open after the wide bar
rather than that bar's close.  One entry per wide bar is automatic:
each wide bar emits a single-bar signal and the harness holds one
position at a time.

Caveat (by design): this fades wide bars, so it loses in runaway
trends where the wide bar is the start of a leg, not its end.
"""

import pandas as pd

VR_THRESH = 2.0   # shipped: wide-bar threshold
POS_LO = 0.25     # shipped: close in the lower/upper quarter of the bar
POS_HI = 0.75


def add_signals(df: pd.DataFrame, vr_thresh: float = VR_THRESH) -> pd.DataFrame:
    df = df.copy()
    wide = (df["vr"] > vr_thresh).fillna(False)
    bearish = wide & (df["bar_pos"] < POS_LO).fillna(False) \
        & (df["ret5"] < 0).fillna(False)
    bullish = wide & (df["bar_pos"] > POS_HI).fillna(False) \
        & (df["ret5"] > 0).fillna(False)
    df["long_entry"] = bearish.astype(bool)
    df["short_entry"] = bullish.astype(bool)
    df["long_exit"] = bullish.astype(bool)
    df["short_exit"] = bearish.astype(bool)
    return df
