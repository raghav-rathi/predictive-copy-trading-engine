"""SineWave signals (Ehlers' cycle-mode rule).

Long entry:  SineWave crosses above LeadSine.
Short entry: SineWave crosses below LeadSine.
Long exit:   SineWave crosses below LeadSine (opposite cross).
Short exit:  SineWave crosses above LeadSine.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies, so
in practice most positions end on the stop/trail/max-hold before the
opposite cross; the opposite cross is the system-defined exit.

Signal columns are boolean, no NaN, no lookahead (the harness executes
at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = crossed_above(df["sine"], df["lead_sine"]).fillna(False)
    dn = crossed_below(df["sine"], df["lead_sine"]).fillna(False)
    df["long_entry"] = up.astype(bool)
    df["short_entry"] = dn.astype(bool)
    df["long_exit"] = dn.astype(bool)
    df["short_exit"] = up.astype(bool)
    return df
