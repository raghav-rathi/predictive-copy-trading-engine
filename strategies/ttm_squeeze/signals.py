"""TTM Squeeze signals.

Entry: the release bar -- first bar where BB expands outside KC after
>= 5 consecutive squeeze bars. Long when the momentum histogram is
rising on the release bar, short when it is falling.
Exit: 2 consecutive momentum-fade bars against the position
(momentum histogram falling twice in a row exits a long, and mirror).
Risk-level exits (stop, max hold) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    prev_squeeze = df["squeeze"].shift(1).fillna(False)
    prev_count = df["squeeze_count"].shift(1).fillna(0)
    fire = prev_squeeze & (~df["squeeze"]) & (prev_count >= 5)
    df["long_entry"] = (fire & df["mom_rising"]).fillna(False)
    df["short_entry"] = (fire & df["mom_falling"]).fillna(False)
    fade_long = (df["mom_falling"] & df["mom_falling"].shift(1).fillna(False)).fillna(False)
    fade_short = (df["mom_rising"] & df["mom_rising"].shift(1).fillna(False)).fillna(False)
    df["long_exit"] = fade_long
    df["short_exit"] = fade_short
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
