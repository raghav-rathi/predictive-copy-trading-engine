"""Three-line break turnaround signals.

Long on the bearish-to-bullish turnaround: the line direction flips
-1 -> +1 (a new white line after a black sequence). Short on the
+1 -> -1 flip. Exits on the opposite flip -- the line-break structure
itself manages the trade, so long_exit is the short-entry flip and
short_exit is the long-entry flip.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    d = df["tlb_dir"].fillna(1.0)
    prev = d.shift(1).fillna(d.iloc[0] if len(d) else 1.0)
    long_entry = ((d == 1) & (prev == -1)).fillna(False)
    short_entry = ((d == -1) & (prev == 1)).fillna(False)
    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    df["long_exit"] = short_entry.astype(bool)
    df["short_exit"] = long_entry.astype(bool)
    return df
