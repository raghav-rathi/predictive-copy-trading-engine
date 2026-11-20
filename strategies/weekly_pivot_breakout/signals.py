"""Prior-week range breakout signals.

Long entry:  close above the prior-week high.
Short entry: close below the prior-week low.
Long exit:   close back inside the prior-week range (close below
             the prior-week high).
Short exit:  close back inside the prior-week range (close above
             the prior-week low).

An opposite breakout is itself a close back inside the range for
the other side (a close below the prior-week low is also below the
prior-week high), so the opposite breakout exits the open trade.
Only one position at a time (harness rule). Signal columns are
boolean, no NaN, no lookahead (the harness executes at the next
bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    ph = df["prior_week_high"]
    pl = df["prior_week_low"]
    df["long_entry"] = (c > ph).fillna(False).astype(bool)
    df["short_entry"] = (c < pl).fillna(False).astype(bool)
    df["long_exit"] = (c < ph).fillna(False).astype(bool)
    df["short_exit"] = (c > pl).fillna(False).astype(bool)
    return df
