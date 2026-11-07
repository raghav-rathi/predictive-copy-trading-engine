"""Bill Williams fractal breakout + Alligator filter signals.

Long: the close crosses above the most recent confirmed up-fractal
high while price is above the Alligator teeth and the Alligator is
awake pointing up (lips > teeth > jaw). Short is the mirror: close
crosses below the most recent confirmed down-fractal low while price
is below the teeth and lips < teeth < jaw. Exit on the reverse
fractal break (close crossing below the most recent down-fractal low
for longs, above the most recent up-fractal high for shorts).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    up = df["frac_up_high"].to_numpy()
    down = df["frac_down_low"].to_numpy()
    teeth = df["alligator_teeth"].to_numpy()
    jaw = df["alligator_jaw"].to_numpy()
    lips = df["alligator_lips"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    for i in range(1, n):
        awake_long = (
            np.isfinite(lips[i]) and lips[i] > teeth[i] and teeth[i] > jaw[i]
        )
        awake_short = (
            np.isfinite(lips[i]) and lips[i] < teeth[i] and teeth[i] < jaw[i]
        )
        if (
            np.isfinite(up[i])
            and np.isfinite(up[i - 1])
            and c[i] > up[i]
            and c[i - 1] <= up[i - 1]
            and np.isfinite(teeth[i])
            and c[i] > teeth[i]
            and awake_long
        ):
            long_entry[i] = True
        if (
            np.isfinite(down[i])
            and np.isfinite(down[i - 1])
            and c[i] < down[i]
            and c[i - 1] >= down[i - 1]
            and np.isfinite(teeth[i])
            and c[i] < teeth[i]
            and awake_short
        ):
            short_entry[i] = True
        if (
            np.isfinite(down[i])
            and np.isfinite(down[i - 1])
            and c[i] < down[i]
            and c[i - 1] >= down[i - 1]
        ):
            long_exit[i] = True
        if (
            np.isfinite(up[i])
            and np.isfinite(up[i - 1])
            and c[i] > up[i]
            and c[i - 1] <= up[i - 1]
        ):
            short_exit[i] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
