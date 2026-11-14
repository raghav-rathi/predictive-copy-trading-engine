"""Kase Peak Oscillator / KaseCD signals (Cynthia Kase).

    long_entry  = KaseCD crosses above 0 while PeakOsc < PeakMax
                  (momentum turning up before the overextension bound)
    short_entry = KaseCD crosses below 0 while PeakOsc > -PeakMax
                  (the -PeakMax leg is vacuous given PeakOsc >= 0, so
                  this is effectively every KCD cross-down; see README)
    long_exit   = KCD crosses below 0, OR PeakOut: PeakOsc was above
                  PeakMax and has pulled back inside it
    short_exit  = KCD crosses above 0, OR the mirror PeakOut (PeakOsc
                  was below -PeakMax and pulled back inside -- cannot
                  fire given PeakOsc >= 0; documented, not hidden)

PeakOut is evaluated on the previous bar's excursion so the exit
fires on the first bar back inside the bound, using only data
through that bar's close. No exit-on-first-weakness: a KCD cross
is a confirmed turn of the oscillator against its own average,
not a one-bar wobble.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    osc = df["kase_peak_osc"]
    kcd = df["kase_cd"]
    pmax = df["kase_peak_max"]

    cross_up = crossed_above(kcd, 0).fillna(False)
    cross_dn = crossed_below(kcd, 0).fillna(False)

    # PeakOut: excursion beyond the bound on a prior bar, now back inside.
    was_above = (osc.shift(1) > pmax.shift(1)).fillna(False)
    back_inside = (osc <= pmax).fillna(False)
    peak_out_long = was_above & back_inside
    # Mirror for shorts: below -PeakMax, then back inside. PeakOsc >= 0
    # by construction, so this leg never fires; kept literal per spec.
    was_below = (osc.shift(1) < -pmax.shift(1)).fillna(False)
    back_inside_dn = (osc >= -pmax).fillna(False)
    peak_out_short = was_below & back_inside_dn

    df["long_entry"] = (cross_up & (osc < pmax)).fillna(False).astype(bool)
    df["short_entry"] = (cross_dn & (osc > -pmax)).fillna(False).astype(bool)
    df["long_exit"] = (cross_dn | peak_out_long).fillna(False).astype(bool)
    df["short_exit"] = (cross_up | peak_out_short).fillna(False).astype(bool)
    return df
