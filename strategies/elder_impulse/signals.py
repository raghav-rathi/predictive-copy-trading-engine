"""Elder Impulse System signals (Alexander Elder, "Come Into My Trading Room").

Long on green bars, short on red bars, flat otherwise: long exits when the
bar is not green (flip to blue or red), short exits when the bar is not red.
Risk-level exits (stop, max hold) come from risk.py.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    color = df["impulse_color"]
    df["long_entry"] = (color == "green").fillna(False)
    df["short_entry"] = (color == "red").fillna(False)
    df["long_exit"] = (color != "green").fillna(False)
    df["short_exit"] = (color != "red").fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
