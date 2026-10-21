"""Know Sure Thing (KST) signal-line cross signals.

Pring's canonical trigger is the KST crossing its 9-bar signal line.
To keep entries aligned with momentum (not chasing late extensions),
entries are gated on the KST's sign:
    long_entry  = crossed_above(kst, kst_signal) & (kst < 0)
    short_entry = crossed_below(kst, kst_signal) & (kst > 0)
i.e. buy a bullish cross only while KST is still below zero (early in
the turn), sell a bearish cross only while KST is still above zero.
Exits are the opposite cross (ungated): long exits on
crossed_below, short on crossed_above.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    k = df["kst"]
    s = df["kst_signal"]
    cross_up = crossed_above(k, s).fillna(False)
    cross_dn = crossed_below(k, s).fillna(False)
    neg = (k < 0).fillna(False)
    pos = (k > 0).fillna(False)

    df["long_entry"] = (cross_up & neg).astype(bool)
    df["short_entry"] = (cross_dn & pos).astype(bool)
    df["long_exit"] = cross_dn.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
