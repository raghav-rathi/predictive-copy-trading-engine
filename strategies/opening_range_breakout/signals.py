"""Opening-range breakout signals.

Long  when close crosses above the day's opening-range high (after the
      OR is complete)
Short when close crosses below the day's opening-range low
No signal exits — the fixed TP/SL in the risk layer handles exits
(one trade per direction per day at most, enforced by the harness's
single-position rule).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    valid = df["or_high"].notna()
    df["long_entry"] = crossed_above(df["c"], df["or_high"]) & valid
    df["short_entry"] = crossed_below(df["c"], df["or_low"]) & valid
    df["long_exit"] = False
    df["short_exit"] = False
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
