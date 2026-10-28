"""Cypher pattern signals.

Enter on pattern completion: long on a bullish Cypher completion
bar, short on a bearish one (the harness executes at the next
bar's open, so the entry lands just after the D pivot confirms).

Exit: the opposite pattern's completion, or the 168-bar max hold
in the risk config — nothing else. There is deliberately no
pattern-failure signal exit: a Cypher D that has not turned is
left to the 2xATR stop / 2.5xATR trail. Boolean columns, no NaN,
no lookahead (completions read confirmed pivots only).
"""

import numpy as np
import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    n = len(df)
    direction = df["cypher_dir"].fillna(0).to_numpy(dtype=int)

    le = np.zeros(n, dtype=bool)
    se = np.zeros(n, dtype=bool)
    lx = np.zeros(n, dtype=bool)
    sx = np.zeros(n, dtype=bool)

    pos = None  # "long" / "short"
    for i in range(n):
        d = int(direction[i])
        if pos == "long" and d == -1:
            lx[i] = True
            pos = None
        elif pos == "short" and d == 1:
            sx[i] = True
            pos = None
        if pos is None and d != 0:
            if d == 1:
                le[i] = True
                pos = "long"
            else:
                se[i] = True
                pos = "short"

    df["long_entry"] = le
    df["short_entry"] = se
    df["long_exit"] = lx
    df["short_exit"] = sx
    return df
