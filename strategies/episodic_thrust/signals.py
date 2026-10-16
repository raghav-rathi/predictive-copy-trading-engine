"""Episodic-pivot signals — LONG ONLY (Bonde's setups are long).

Entry on the thrust-bar close (executed at the next open). Exit on the
first down bar (close < prior close) after 3+ consecutive up bars — the
"first down day" exit — or via risk stops / 30-bar max hold.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    up = (df["c"] > df["c"].shift(1)).astype(int)
    streak = up.groupby((up == 0).cumsum()).cumsum()

    df["long_entry"] = df["thrust"]
    df["short_entry"] = pd.Series(False, index=df.index)
    df["short_exit"] = pd.Series(False, index=df.index)
    df["long_exit"] = (
        (df["c"] < df["c"].shift(1)) & (streak.shift(1) >= 3)
    ).fillna(False).astype(bool)
    return df
