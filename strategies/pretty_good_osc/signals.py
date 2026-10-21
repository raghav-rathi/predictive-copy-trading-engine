"""Pretty Good Oscillator signals.

Entry is a breakout trigger on the oscillator:
  long_entry  = PGO crosses above +3.0  (close thrust >3 ATR above the SMA)
  short_entry = PGO crosses below -3.0  (close thrust >3 ATR below the SMA)

Exits take the trade off when the displacement decays back through the
mean:
  long_exit  = PGO crosses below 0  (close fell back to its 14-bar SMA)
  short_exit = PGO crosses above 0

The threshold columns are read from df["pgo_trigger"] (a scalar
carried by the indicator frame) so calibration sweeps can move the
trigger without touching the signal logic.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pgo = df["pgo"]
    thr = float(df["pgo_trigger"].iloc[-1]) if "pgo_trigger" in df else 3.0
    thr_s = pd.Series(thr, index=df.index)
    neg_s = pd.Series(-thr, index=df.index)
    zero_s = pd.Series(0.0, index=df.index)

    cross_up_thr = crossed_above(pgo, thr_s).fillna(False)
    cross_dn_thr = crossed_below(pgo, neg_s).fillna(False)
    cross_dn_zero = crossed_below(pgo, zero_s).fillna(False)
    cross_up_zero = crossed_above(pgo, zero_s).fillna(False)

    df["long_entry"] = cross_up_thr.astype(bool)
    df["short_entry"] = cross_dn_thr.astype(bool)
    df["long_exit"] = cross_dn_zero.astype(bool)
    df["short_exit"] = cross_up_zero.astype(bool)
    return df
