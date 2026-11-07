"""1-2-3 Reversal signals.

Long: a bullish 1-2-3 is active (point 3 confirmed, holding above point
1) and the close breaks above point 2 — enter on that bar, once per
pattern. Exit long on a close below point 3 (invalidation) or on an
opposite (bearish) 1-2-3 completion (close below the bearish point 2).
Short is the mirror image. Point-3 exit levels are latched at entry
because the pattern clears from the indicator columns once it completes.
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    c = df["c"].to_numpy()
    bullish = df["otr_bullish"].to_numpy()
    bearish = df["otr_bearish"].to_numpy()
    bull_p2 = df["otr_bull_p2"].to_numpy()
    bull_p3 = df["otr_bull_p3"].to_numpy()
    bull_complete = df["otr_bull_complete"].to_numpy()
    bear_p2 = df["otr_bear_p2"].to_numpy()
    bear_p3 = df["otr_bear_p3"].to_numpy()
    bear_complete = df["otr_bear_complete"].to_numpy()
    long_entry = np.zeros(n, dtype=bool)
    short_entry = np.zeros(n, dtype=bool)
    long_exit = np.zeros(n, dtype=bool)
    short_exit = np.zeros(n, dtype=bool)
    entered: set[int] = set()
    latched_p3_long = None
    latched_p3_short = None
    for i in range(n):
        # Opposite-pattern completion on this bar (close through its p2).
        bull_done = bool(
            bullish[i] == 1.0 and np.isfinite(bull_p2[i]) and c[i] > bull_p2[i]
        )
        bear_done = bool(
            bearish[i] == 1.0 and np.isfinite(bear_p2[i]) and c[i] < bear_p2[i]
        )
        if (
            bullish[i] == 1.0
            and np.isfinite(bull_p2[i])
            and np.isfinite(bull_complete[i])
            and int(bull_complete[i]) not in entered
            and c[i] > bull_p2[i]
        ):
            long_entry[i] = True
            entered.add(int(bull_complete[i]))
            latched_p3_long = float(bull_p3[i]) if np.isfinite(bull_p3[i]) else None
        elif (
            bearish[i] == 1.0
            and np.isfinite(bear_p2[i])
            and np.isfinite(bear_complete[i])
            and int(bear_complete[i]) not in entered
            and c[i] < bear_p2[i]
        ):
            short_entry[i] = True
            entered.add(int(bear_complete[i]))
            latched_p3_short = float(bear_p3[i]) if np.isfinite(bear_p3[i]) else None
        # Exits: close through the latched point 3, or opposite completion.
        if latched_p3_long is not None and c[i] < latched_p3_long:
            long_exit[i] = True
            latched_p3_long = None
        if bear_done and latched_p3_long is not None:
            long_exit[i] = True
            latched_p3_long = None
        if latched_p3_short is not None and c[i] > latched_p3_short:
            short_exit[i] = True
            latched_p3_short = None
        if bull_done and latched_p3_short is not None:
            short_exit[i] = True
            latched_p3_short = None
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
