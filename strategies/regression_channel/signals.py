"""Linear regression channel signals (mean reversion).

Long entry:  close crosses back above the lower band (coming up from
             below/at the band).
Short entry: close crosses back below the upper band.
Long exit:   close crosses back above the regression midline.
Short exit:  close crosses back below the regression midline.

The entry is the cross-BACK, not the touch: price must first go to
(or through) the band and then return inside it. The exit is the
first cross of the midline, so a trade that reverts cleanly banks the
move from the band to the centre; a trade that never reaches the
midline is left to the harness stop/trail.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = B.crossed_above(df["c"], df["reg_lower"]).fillna(False).astype(bool)
    df["short_entry"] = B.crossed_below(df["c"], df["reg_upper"]).fillna(False).astype(bool)
    df["long_exit"] = B.crossed_above(df["c"], df["reg_mid"]).fillna(False).astype(bool)
    df["short_exit"] = B.crossed_below(df["c"], df["reg_mid"]).fillna(False).astype(bool)
    return df
