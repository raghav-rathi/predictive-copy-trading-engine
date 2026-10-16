"""Ehlers RVI signals.

  long_entry:  RVI crosses above its signal line
  short_entry: RVI crosses below its signal line

Optional whipsaw filter (min_sep > 0): only take the cross when the
RVI/signal separation at the cross bar exceeds min_sep. The shipped
config uses no filter; the 0.02 variant is tested in CALIBRATION.md.
Exits are risk-managed (2xATR stop, 72-bar max hold).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame, min_sep: float = 0.0) -> pd.DataFrame:
    df = df.copy()
    rvi, sig = df["rvi"], df["rvi_signal"]

    cross_up = B.crossed_above(rvi, sig)
    cross_dn = B.crossed_below(rvi, sig)
    if min_sep > 0:
        sep = (rvi - sig).abs() >= min_sep
        cross_up = cross_up & sep.fillna(False)
        cross_dn = cross_dn & sep.fillna(False)

    df["long_entry"] = cross_up.fillna(False).astype(bool)
    df["short_entry"] = cross_dn.fillna(False).astype(bool)
    df["long_exit"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    return df
