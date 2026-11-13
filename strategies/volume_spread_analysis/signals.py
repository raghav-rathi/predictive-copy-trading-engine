"""Volume Spread Analysis signals (Tom Williams, Master the Markets).

Long entry:  NO-SUPPLY bar or STOPPING VOLUME bar.
Short entry: NO-DEMAND bar or UPTHRUST bar.
Long exit:   the opposite VSA signal (no-demand or upthrust).
Short exit:  the opposite VSA signal (no-supply or stopping volume).

An exit is never fired on the same bar as an entry in the same
direction (a bar cannot be both a long and a short VSA pattern in
practice — no-supply/stopping-volume need a down bar, no-demand
needs an up bar — but upthrust can coincide with stopping volume
on a down bar that probed above the 20-bar high, so the exit is
masked by the same-direction entry on such a bar).

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_sig = df["vsa_no_supply"] | df["vsa_stopping_volume"]
    short_sig = df["vsa_no_demand"] | df["vsa_upthrust"]
    df["long_entry"] = long_sig.fillna(False).astype(bool)
    df["short_entry"] = short_sig.fillna(False).astype(bool)
    df["long_exit"] = (short_sig & ~long_sig).fillna(False).astype(bool)
    df["short_exit"] = (long_sig & ~short_sig).fillna(False).astype(bool)
    return df
