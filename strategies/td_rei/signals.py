"""DeMark Range Expansion Index (TD REI) signals.

Long: REI crosses above -60 from below (oversold snap-back).
Short: REI crosses below +60 from above (overbought roll-over).
Exit a long on the opposite extreme cross (REI crossing below +60);
exit a short on REI crossing above -60. All inputs are computed from
data through bar i's close, so signals on bar i use no future data.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

LONG_LEVEL = -60.0
SHORT_LEVEL = 60.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    rei = df["rei"]
    cross_up = crossed_above(rei, LONG_LEVEL).fillna(False)
    cross_down = crossed_below(rei, SHORT_LEVEL).fillna(False)
    df["long_entry"] = cross_up.astype(bool)
    df["short_entry"] = cross_down.astype(bool)
    df["long_exit"] = cross_down.astype(bool)
    df["short_exit"] = cross_up.astype(bool)
    return df
