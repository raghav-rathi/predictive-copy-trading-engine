"""5-0 Pattern signals.

Bullish: after C completes, D is the 50% retracement of the BC leg.
Enter long on the first bar (within 20 bars of C's completion) where
the close reaches the D level with reversal confirmation (close >
open AND close > previous close). Exit long when the close reaches
the 38.2% retracement of the BC leg measured from B (C + 0.618*BC),
which sits above the D entry. Bearish is the mirror image.
"""

import numpy as np
import pandas as pd

ENTRY_WINDOW_BARS = 20


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    o = df["o"].to_numpy()
    c = df["c"].to_numpy()
    bullish = df["fz_bullish"].to_numpy()
    bearish = df["fz_bearish"].to_numpy()
    d_level = df["fz_d_level"].to_numpy()
    exit_long = df["fz_exit_long"].to_numpy()
    exit_short = df["fz_exit_short"].to_numpy()
    complete = df["fz_complete"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    entered: set[int] = set()
    for i in range(1, n):
        if np.isfinite(complete[i]):
            comp = int(complete[i])
            if comp not in entered and comp < i <= comp + ENTRY_WINDOW_BARS:
                if (
                    bullish[i] == 1.0
                    and np.isfinite(d_level[i])
                    and c[i] >= d_level[i]
                    and c[i] > o[i]
                    and c[i] > c[i - 1]
                ):
                    long_entry[i] = True
                    entered.add(comp)
                elif (
                    bearish[i] == 1.0
                    and np.isfinite(d_level[i])
                    and c[i] <= d_level[i]
                    and c[i] < o[i]
                    and c[i] < c[i - 1]
                ):
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
