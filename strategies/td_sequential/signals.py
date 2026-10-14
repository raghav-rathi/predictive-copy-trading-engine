"""TD Sequential signals.

Long entry:  bar completing a perfected + qualified buy countdown.
Long exit:   opposite (sell) countdown completes, or close breaks TDST support.
Mirror for shorts.

Note on timing: the completion is known at bar i's close; the harness
executes at bar i+1's open, so the fill is the next open, not the signal
close — documented as an approximation.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["long_entry"] = df["buy_cd_done"]
    df["short_entry"] = df["sell_cd_done"]
    tdst_break_dn = df["c"] < df["tdst_s"]
    tdst_break_up = df["c"] > df["tdst_r"]
    df["long_exit"] = df["sell_cd_done"] | tdst_break_dn
    df["short_exit"] = df["buy_cd_done"] | tdst_break_up
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
