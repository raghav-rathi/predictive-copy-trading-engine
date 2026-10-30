"""Money Flow Index signals.

    long_entry  -- MFI crosses back above 20 from below
                   (oversold recovery)
    short_entry -- MFI crosses back below 80 from above
                   (overbought fade)
    long_exit   -- MFI crosses below the 50 midline
    short_exit  -- MFI crosses above the 50 midline

Entries wait for the turn, not the touch: a long fires only
when MFI was at/below 20 on the prior bar and is above 20
now, so a market sliding deeper into oversold territory does
not keep re-entering. Exits use the midline cross against
the position. NaN comparisons are False, so no signal fires
before MFI exists. Boolean columns, no NaN, no lookahead.
"""

import pandas as pd

from strategies import base as B

OVERSOLD = 20.0
OVERBOUGHT = 80.0
MIDLINE = 50.0


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    mfi = df["mfi"]
    df["long_entry"] = B.crossed_above(mfi, OVERSOLD).fillna(False).to_numpy(dtype=bool)
    df["short_entry"] = B.crossed_below(mfi, OVERBOUGHT).fillna(False).to_numpy(dtype=bool)
    df["long_exit"] = B.crossed_below(mfi, MIDLINE).fillna(False).to_numpy(dtype=bool)
    df["short_exit"] = B.crossed_above(mfi, MIDLINE).fillna(False).to_numpy(dtype=bool)
    return df
