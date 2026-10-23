"""SMI Ergodic oscillator / signal-line crossover, zone-gated.

Blau's classic SMI Ergodic trade: act on crosses of the oscillator
with its 5-bar signal line ONLY when the cross starts from the
relevant extreme zone — the cross must mean-revert FROM oversold
(buy) or overbought (sell), not chop in the mid-band:

    long_entry  = crossed_above(smi, smi_signal) & (smi.shift(1) <= -40)
    short_entry = crossed_below(smi, smi_signal) & (smi.shift(1) >= +40)
    long_exit   = crossed_below(smi, smi_signal)
    short_exit  = crossed_above(smi, smi_signal)

The zone gate reads the PRIOR bar's smi: crossed_above at bar j
already tells us smi_{j-1} <= signal_{j-1}, and the additional
smi_{j-1} <= -40 says the cross began deep in oversold territory —
the classic Blau "hook out of the zone". Exits are the plain
opposite cross (the momentum turn is the edge; no fixed target).

Signal columns are boolean, no NaN, no lookahead: the cross at bar
j uses data through bar j's close, and the harness executes at the
next bar's open.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below
from strategies.smi_ergodic.indicators import ZONE


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    smi = df["smi"]
    sig = df["smi_signal"]
    up = crossed_above(smi, sig).fillna(False)
    dn = crossed_below(smi, sig).fillna(False)
    oversold_prior = (smi.shift(1) <= -ZONE).fillna(False)
    overbought_prior = (smi.shift(1) >= ZONE).fillna(False)
    df["long_entry"] = (up & oversold_prior).astype(bool)
    df["short_entry"] = (dn & overbought_prior).astype(bool)
    df["long_exit"] = dn.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
