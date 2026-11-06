"""Three Drives Pattern signals.

Bullish: enter long on the first bar after D3 completes (within 10
bars) where close > open AND close > previous close. Exit long when
the close reaches D3 + 0.618 * (drive-start high - D3). Bearish is
the mirror image. D3 completes 2 bars after its pivot bar, so the
entry bar is strictly after the pattern is knowable.
"""

import numpy as np
import pandas as pd

ENTRY_WINDOW_BARS = 10


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy()
    c = df["c"].to_numpy()
    bullish = df["td_bullish"].to_numpy()
    bearish = df["td_bearish"].to_numpy()
    exit_long = df["td_exit_long"].to_numpy()
    exit_short = df["td_exit_short"].to_numpy()
    complete = df["td_complete"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    entered: set[int] = set()
    for i in range(1, n):
        if np.isfinite(complete[i]):
            comp = int(complete[i])
            if comp not in entered and comp < i <= comp + ENTRY_WINDOW_BARS:
                if bullish[i] == 1.0 and c[i] > o[i] and c[i] > c[i - 1]:
                    long_entry[i] = True
                    entered.add(comp)
                elif bearish[i] == 1.0 and c[i] < o[i] and c[i] < c[i - 1]:
                    short_entry[i] = True
                    entered.add(comp)
        if np.isfinite(exit_long[i]) and c[i] >= exit_long[i]:
            long_exit[i] = True
        if np.isfinite(exit_short[i]) and c[i] <= exit_short[i]:
            short_exit[i] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
