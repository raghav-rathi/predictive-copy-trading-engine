"""Wolfe Wave signals.

Bullish: after point 5 completes (low breaking below the 1-3 trendline),
enter long on the first close back above the 1-3 trendline within
20 bars of completion. Exit long when the close reaches the EPA line
(line through points 1 and 4). Bearish is the mirror image.
Trendline values come from pivots confirmed before the current bar,
so a close crossing a trendline uses only past pivot geometry.
"""

import numpy as np
import pandas as pd

ENTRY_WINDOW_BARS = 20


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    line13 = df["ww_line13"].to_numpy()
    epa = df["ww_epa"].to_numpy()
    bullish = df["ww_bullish"].to_numpy()
    bearish = df["ww_bearish"].to_numpy()
    complete = df["ww_complete"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    for i in range(1, n):
        if np.isfinite(complete[i]):
            age = i - int(complete[i])
            if bullish[i] == 1.0 and 0 <= age <= ENTRY_WINDOW_BARS:
                if (
                    np.isfinite(line13[i])
                    and np.isfinite(line13[i - 1])
                    and c[i] > line13[i]
                    and c[i - 1] <= line13[i - 1]
                ):
                    long_entry[i] = True
            if bearish[i] == 1.0 and 0 <= age <= ENTRY_WINDOW_BARS:
                if (
                    np.isfinite(line13[i])
                    and np.isfinite(line13[i - 1])
                    and c[i] < line13[i]
                    and c[i - 1] >= line13[i - 1]
                ):
                    short_entry[i] = True
        if bullish[i] == 1.0 and np.isfinite(epa[i]) and c[i] >= epa[i]:
            long_exit[i] = True
        if bearish[i] == 1.0 and np.isfinite(epa[i]) and c[i] <= epa[i]:
            short_exit[i] = True
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
